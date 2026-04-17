import sys, os
backend_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, backend_dir)
for a in ["sponsor_agent", "artist_agent", "exhibitor_agent", "venue_agent", "pricing_agent", "community_agent", "instagram_agent"]:
    sys.path.append(os.path.join(backend_dir, "agents", a))

from flask import Flask, request, jsonify
import uuid
from flask_cors import CORS
from agents.orchestrator_agent import OrchestratorAgent

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)

# In-memory storage for orchestrator sessions. 
# For production, consider using Redis or a database to store session states.
orchestrator_sessions = {}

@app.route('/api/init_and_sponsor', methods=['POST'])
def init_and_sponsor():
    """
    Receives the initial prompt, creates an Orchestrator, extracts info,
    and calls the sponsor agent. Returns the session_id and sponsors.
    """
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Missing 'prompt' in the request JSON"}), 400

    user_prompt = data['prompt']
    
    try:
        session_id = str(uuid.uuid4())
        orchestrator = OrchestratorAgent()
        
        # 1. Extract Details
        orchestrator.extracted_info = orchestrator.extract_parameters(user_prompt)
        
        # 2. Call Sponsor Agent
        print("calling sponsor agent")
        sponsors = orchestrator.call_sponsor_agent(memory=orchestrator.memory)
        
        # Store in session
        orchestrator_sessions[session_id] = orchestrator
        
        print("done all, returning from innit")
        
        return jsonify({
            "session_id": session_id,
            "extracted_info": dict(orchestrator.extracted_info) if orchestrator.extracted_info else {},
            "sponsors": sponsors
        }), 200

    except Exception as e:
        print(f"Error during init and sponsor: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/speaker', methods=['POST'])
def get_speakers():
    data = request.get_json()
    session_id = data.get('session_id')
    
    if not session_id or session_id not in orchestrator_sessions:
        return jsonify({"error": "Invalid or missing session_id"}), 400
        
    orchestrator = orchestrator_sessions[session_id]
    
    try:
        # Assuming location, budget, audience_size were extracted
        location = orchestrator.extracted_info.location if orchestrator.extracted_info else "Unknown Location"
        budget = orchestrator.extracted_info.budget if orchestrator.extracted_info else 0.0
        audience_size = orchestrator.extracted_info.target_audience_size if orchestrator.extracted_info else 0
        
        speakers = orchestrator.call_artist_agent(
            location=location,
            budget=budget,
            audience_size=audience_size,
            memory=orchestrator.memory
        )
        return jsonify({"speakers_artists": speakers}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/exhibitor', methods=['POST'])
def get_exhibitors():
    data = request.get_json()
    session_id = data.get('session_id')
    
    if not session_id or session_id not in orchestrator_sessions:
        return jsonify({"error": "Invalid or missing session_id"}), 400
        
    orchestrator = orchestrator_sessions[session_id]
    
    try:
        exhibitors = orchestrator.call_exhibitor_agent(memory=orchestrator.memory)
        return jsonify({"exhibitors": exhibitors}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/venue', methods=['POST'])
def get_venues():
    data = request.get_json()
    session_id = data.get('session_id')
    
    if not session_id or session_id not in orchestrator_sessions:
        return jsonify({"error": "Invalid or missing session_id"}), 400
        
    orchestrator = orchestrator_sessions[session_id]
    
    try:
        venues = orchestrator.call_venue_agent(memory=orchestrator.memory)
        return jsonify({"venues": venues}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/pricing', methods=['POST'])
def get_pricing():
    data = request.get_json()
    session_id = data.get('session_id')
    
    if not session_id or session_id not in orchestrator_sessions:
        return jsonify({"error": "Invalid or missing session_id"}), 400
        
    orchestrator = orchestrator_sessions[session_id]
    
    try:
        pricing = orchestrator.call_pricing_agent(memory=orchestrator.memory)
        return jsonify({"pricing": pricing}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/community', methods=['POST'])
def get_communities():
    data = request.get_json()
    session_id = data.get('session_id')
    
    if not session_id or session_id not in orchestrator_sessions:
        return jsonify({"error": "Invalid or missing session_id"}), 400
        
    orchestrator = orchestrator_sessions[session_id]
    
    try:
        communities = orchestrator.call_community_agent(memory=orchestrator.memory)
        return jsonify({"communities": communities}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/schedule', methods=['POST'])
def get_schedule():
    data = request.get_json()
    session_id = data.get('session_id')
    
    if not session_id or session_id not in orchestrator_sessions:
        return jsonify({"error": "Invalid or missing session_id"}), 400
        
    orchestrator = orchestrator_sessions[session_id]
    
    try:
        schedule = orchestrator.build_event_schedule(memory=orchestrator.memory)
        return jsonify({"schedule": schedule}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)