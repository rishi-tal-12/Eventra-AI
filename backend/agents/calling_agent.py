import json
import base64
import threading
import audioop
import numpy as np
import whisper

from flask import Response, request
from flask_sock import Sock
from twilio.twiml.voice_response import VoiceResponse, Connect
from twilio.rest import Client as TwilioClient
from piper.voice import PiperVoice

from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from config import GROQ_API_KEY, NGROK_HOST, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM, TWILIO_TO
from tools import ALL_TOOLS

BASE_SYSTEM_PROMPT = """You are a helpful voice assistant on a phone call.
Keep your responses concise and conversational — this is spoken audio, not text.
Avoid bullet points, markdown, or long paragraphs.
Respond naturally as if speaking to the caller."""


class TwilioAgent:
    def __init__(self, app):
        """
        Pass in the existing Flask app instance — no new Flask app is created.
        """
        self.app = app
        self.sock = Sock(app)  # attaches flask-sock to your existing app

        self.tw_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        # Piper TTS
        self.global_piper_voice = PiperVoice.load("agents/static/en_US-danny-low.onnx")

        # Whisper STT
        print("Loading Whisper model...")
        self.whisper_model = whisper.load_model("base")
        print("Whisper model loaded.")

        # LLM (shared across calls — the agent graph is built per-call with its own prompt)
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=GROQ_API_KEY,
            temperature=0.7,
        )
        print("LLM ready.")

        # Per-call state keyed by Twilio Call SID
        # Each entry: { "call_purpose": str, "starting_conversation": str, "agent": agent }
        self._active_calls = {}
        self._calls_lock = threading.Lock()

        self._register_routes()

    def _build_agent_for_call(self, call_purpose: str):
        """Build a LangGraph react agent with a purpose-aware system prompt."""
        prompt = BASE_SYSTEM_PROMPT
        if call_purpose:
            prompt += (
                f"\n\n--- CALL PURPOSE ---\n"
                f"{call_purpose}\n"
                f"Stay focused on this purpose throughout the conversation. "
                f"Guide the dialogue toward fulfilling this objective."
            )

        # Reference: https://langchain-ai.github.io/langgraph/how-tos/create-react-agent/
        agent = create_react_agent(
            self.llm,
            tools=ALL_TOOLS,
            prompt=prompt,
        )
        return agent

    def _register_routes(self):
        # HTTP route — uses self.app directly
        self.app.add_url_rule(
            "/twilio-webhook",
            view_func=self.twilio_webhook,
            methods=["POST"]
        )
        # WebSocket route — uses self.sock
        self.sock.route("/audiostream")(self.audio_stream)

    def twilio_webhook(self):
        response = VoiceResponse()
        connect = Connect()
        connect.stream(url=f"wss://{NGROK_HOST}/audiostream")
        response.append(connect)
        return Response(str(response), mimetype='text/xml')

    def make_call(self, starting_conversation: str = "", call_purpose: str = "", phone_number: str = ""):
        """
        Initiate an outbound call driven by a purpose and opening line.

        Args:
            starting_conversation: The first thing the agent will say when the
                call connects (e.g. "Hi, this is Alex from Eventra…").
            call_purpose: A high-level objective that steers the LLM throughout
                the call (e.g. "Confirm the vendor's availability for June 15
                and negotiate pricing for a 200-person catering package.").
            phone_number: The number to dial. Falls back to TWILIO_TO from
                config if not provided.
        """
        to_number = phone_number or TWILIO_TO
        print(f"Dialing {to_number}...")
        call = self.tw_client.calls.create(
            to=to_number,
            from_=TWILIO_FROM,
            url=f"https://{NGROK_HOST}/twilio-webhook",
        )
        print(f"Call initiated. SID: {call.sid}")

        # Store per-call context so the WebSocket handler can pick it up
        agent = self._build_agent_for_call(call_purpose)
        with self._calls_lock:
            self._active_calls[call.sid] = {
                "call_purpose": call_purpose,
                "starting_conversation": starting_conversation,
                "agent": agent,
            }

        return call.sid

    # ------------------------------------------------------------------
    # Helpers to resolve call context from a Twilio stream
    # ------------------------------------------------------------------

    def _get_call_context(self, call_sid: str) -> dict:
        """Retrieve the stored context for a call, or a sensible default."""
        with self._calls_lock:
            ctx = self._active_calls.get(call_sid)
        if ctx:
            return ctx
        # Fallback for inbound calls or calls made without make_call()
        return {
            "call_purpose": "",
            "starting_conversation": "",
            "agent": self._build_agent_for_call(""),
        }

    def _cleanup_call(self, call_sid: str):
        with self._calls_lock:
            self._active_calls.pop(call_sid, None)

    # ------------------------------------------------------------------
    # WebSocket audio stream
    # ------------------------------------------------------------------

    def audio_stream(self, ws):
        print("WebSocket Connection Opened!")
        stream_sid = None
        call_sid = None
        audio_buffer = bytearray()
        chat_history = []
        call_ctx = None
        agent = None
        CHUNK_THRESHOLD = 8000 * 2

        while True:
            message = ws.receive()
            if message is None:
                break

            data = json.loads(message)
            event_type = data.get("event")

            if event_type == "start":
                stream_sid = data["start"]["streamSid"]
                call_sid = data["start"].get("callSid", "")
                print(f"Stream started: {stream_sid}  (call: {call_sid})")

                audio_buffer.clear()
                chat_history.clear()

                # Resolve per-call context
                call_ctx = self._get_call_context(call_sid)
                agent = call_ctx["agent"]
                starting_conversation = call_ctx["starting_conversation"]

                # Speak the opening line and seed chat history
                if starting_conversation:
                    print(f"Opening line: '{starting_conversation}'")
                    chat_history.append(AIMessage(content=starting_conversation))
                    opening_audio = self.generate_twilio_base64_audio(starting_conversation)
                    if opening_audio and stream_sid:
                        ws.send(json.dumps({
                            "event": "media",
                            "streamSid": stream_sid,
                            "media": {"payload": opening_audio},
                        }))

            elif event_type == "media":
                mulaw_bytes = base64.b64decode(data["media"]["payload"])
                audio_buffer.extend(mulaw_bytes)

                if len(audio_buffer) >= CHUNK_THRESHOLD:
                    chunk = bytes(audio_buffer)
                    audio_buffer.clear()
                    threading.Thread(
                        target=self.transcribe_and_respond,
                        args=(chunk, stream_sid, ws, chat_history, agent),
                        daemon=True,
                    ).start()

            elif event_type == "stop":
                print("Stream closed.")
                if call_sid:
                    self._cleanup_call(call_sid)
                break

    def transcribe_and_respond(self, mulaw_bytes, stream_sid, ws, chat_history, agent):
        try:
            pcm_8k = audioop.ulaw2lin(mulaw_bytes, 2)
            pcm_16k, _ = audioop.ratecv(pcm_8k, 2, 1, 8000, 16000, None)
            audio_np = np.frombuffer(pcm_16k, dtype=np.int16).astype(np.float32) / 32768.0

            print("Transcribing...")
            result = self.whisper_model.transcribe(audio_np, language="en", fp16=False)
            transcript = result["text"].strip()
            print(f"Transcript: '{transcript}'")

            if not transcript or len(transcript) == 0:
                print("Empty transcript detected. Skipping LLM call.")
                return

            chat_history.append(HumanMessage(content=transcript))

            # https://langchain-ai.github.io/langgraph/how-tos/create-react-agent/
            agent_result = agent.invoke({
                "messages": chat_history,
            })

            # The result dict contains the updated "messages" list
            updated_messages = agent_result["messages"]

            # The final AI response
            llm_response = ""
            if updated_messages and isinstance(updated_messages[-1], AIMessage):
                llm_response = updated_messages[-1].content.strip()

            print(f"LLM Response: '{llm_response}'")

            # Update history to retain full conversation state
            chat_history.clear()
            chat_history.extend(updated_messages)

            reply_audio = self.generate_twilio_base64_audio(llm_response)
            if reply_audio and stream_sid:
                ws.send(json.dumps({
                    "event": "media",
                    "streamSid": stream_sid,
                    "media": {"payload": reply_audio},
                }))

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"ERROR in transcribe_and_respond: {e}")

    def generate_twilio_base64_audio(self, text: str) -> str:
        try:
            if hasattr(self.global_piper_voice, 'synthesize'):
                raw_pcm_bytes = b"".join(
                    chunk.audio_int16_bytes
                    for chunk in self.global_piper_voice.synthesize(text)
                )
            elif hasattr(self.global_piper_voice, 'synthesize_stream_raw'):
                raw_pcm_bytes = b"".join(self.global_piper_voice.synthesize_stream_raw(text))
            else:
                return ""
        except Exception as e:
            print(f"ERROR in Piper: {e}")
            return ""

        if not raw_pcm_bytes:
            return ""

        try:
            downsampled, _ = audioop.ratecv(
                raw_pcm_bytes, 2, 1,
                self.global_piper_voice.config.sample_rate, 8000, None,
            )
            mulaw = audioop.lin2ulaw(downsampled, 2)
            return base64.b64encode(mulaw).decode('utf-8')
        except Exception as e:
            print(f"ERROR in audio conversion: {e}")
            return ""