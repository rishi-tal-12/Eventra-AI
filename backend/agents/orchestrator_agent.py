import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from config import GEMINI_API_KEY

try:
    from agents.email_bot_agent import email_bot
except ImportError:
    email_bot = None

# Mocking the Supabase client
from supabase import create_client, Client

# Importing other agents based on workspace structure
try:
    from agents.sponsor_agent.agent import SponsorAgent
except ImportError:
    SponsorAgent = None

try:
    from agents.pricing_agent.agent import PricingAgent
except ImportError:
    PricingAgent = None

try:
    from agents.exhibitor_agent.agent import ExhibitorAgent
    from agents.exhibitor_agent.models import RecommendationRequest
except ImportError:
    ExhibitorAgent = None
    RecommendationRequest = None

try:
    from agents.community_agent.agent import recommend_communities
except ImportError:
    recommend_communities = None

try:
    from agents.instagram_agent.core.graph import run_pipeline as run_instagram_pipeline
    from agents.instagram_agent.core.models import EventDetails as InstaEventDetails
except ImportError:
    run_instagram_pipeline = None
    InstaEventDetails = None

from agents.artist_agent.agent import ArtistAgent
from agents.venue_agent.agent import VenueAgent
from agents.calling_agent import TwilioAgent
from tools.search_tool import web_search

# Using LLM for extraction
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import PromptTemplate

class ExtractedInfo(BaseModel):
    description: str = Field(description="Description of the event")
    location: str = Field(description="Location of the event")
    target_audience_type: str = Field(description="Type of the target audience")
    target_audience_size: int = Field(description="Estimated size of the target audience")
    budget: float = Field(description="Budget for the event")

class OrchestratorAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0.7,
        )
        
        # Central memory to store responses of previous agents
        self.memory: Dict[str, Any] = {}
        # Stores parameters extracted from original prompt
        self.extracted_info: Optional[ExtractedInfo] = None
        
        # Initialize Supabase
        supabase_url = os.environ.get("SUPABASE_URL", "")
        supabase_key = os.environ.get("SUPABASE_KEY", "")
        if supabase_url and supabase_key:
            self.supabase: Client = create_client(supabase_url, supabase_key)
        else:
            self.supabase = None
            
        self.artist_agent = ArtistAgent()
        self.venue_agent = VenueAgent()
        self.sponsor_agent = SponsorAgent() if SponsorAgent else None
        self.pricing_agent = PricingAgent() if PricingAgent else None
        
        self.exhibitor_agent = None
        if ExhibitorAgent:
            self.exhibitor_agent = ExhibitorAgent()
            try:
                self.exhibitor_agent.load_data()
            except Exception as e:
                print(f"Failed to load exhibitor agent data: {e}")

        try:
            from flask import current_app
            self.calling_agent = TwilioAgent(
                app=current_app
            ) if hasattr(TwilioAgent, '__init__') else None
        except Exception:
            self.calling_agent = None

    def extract_parameters(self, prompt: str) -> ExtractedInfo:
        """Extract event parameters from the user prompt."""
        extraction_prompt = PromptTemplate.from_template(
            "Extract the following information from the user prompt:\n\n{prompt}\n"
        )
        chain = extraction_prompt | self.llm.with_structured_output(ExtractedInfo)
        return chain.invoke({"prompt": prompt})

    def fetch_previous_events(self, description: str) -> List[Dict[str, Any]]:
        """Fetch previous events from Supabase using semantic search on description."""
        if not self.supabase:
            print("Warning: Supabase credentials not found. Returning empty list.")
            return []
            
        query_embedding = self._get_embedding(description)
        
        # Semantic search using pgvector function on supabase
        response = self.supabase.rpc(
            "match_events", 
            {"query_embedding": query_embedding, "match_threshold": 0.7, "match_count": 5}
        ).execute()
        
        return response.data if response.data else []
        
    def _get_embedding(self, text: str) -> List[float]:
        try:
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            return embeddings.embed_query(text)
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return [0.0] * 1536 # mock

    def acquire_contact_details(self, artist_name: str) -> str:
        """Use web search to find contact details, with a fallback."""
        try:
            # Assuming search_tool returns a string or dict of results
            results = search(f"{artist_name} contact email booking phone number management")
            
            # Simple fallback extraction
            extract_contact_prompt = PromptTemplate.from_template(
                "Extract the email address and phone number for {artist} from the following search results:\n{results}\n\nReturn 'Email: <email>, Phone: <phone>'. If not found, return 'Not found'."
            )
            chain = extract_contact_prompt | self.llm
            contact_info = chain.invoke({"artist": artist_name, "results": results}).content
            return contact_info
        except Exception as e:
            print(f"Search failed for {artist_name}: {e}")
            return "contact.sid.chopra@gmail.com, +919810706119" # Fallback

    def call_artist_agent(self, location: str, budget: float, audience_size: int, memory: dict) -> List[Any]:
        """Calls the artist agent, records the output to memory, and returns it."""
        try:
            print("Calling Artist Agent...")
            artist_results_dict = self.artist_agent.run(
                city=location,
                audience_size=audience_size,
                memory=memory
            )
            # Extracted list of artists mapping from the dict structure returned by ArtistAgent
            artist_results = artist_results_dict.get("top_artists", [])
            self.memory["artist_agent_results"] = artist_results
            return artist_results
        except Exception as e:
            print(f"Failed to use artist agent: {e}")
            fallback = [{"name": "Mock Artist"}]
            self.memory["artist_agent_results"] = fallback
            return fallback

    def call_venue_agent(self, memory: dict) -> List[Any]:
        """Calls the venue agent passing context, records output to memory, and returns it."""
        if not self.extracted_info:
            print("Venue agent missing extracted info.")
            return []
            
        try:
            print("Calling Venue Agent...")
            venue_results_dict = self.venue_agent.run(
                city=self.extracted_info.location,
                event_type=self.extracted_info.target_audience_type, # loosely mapping
                audience_size=self.extracted_info.target_audience_size,
                memory=memory
            )
            
            venues = venue_results_dict.get("top_venues", [])
            self.memory["venue_agent_results"] = venues
            return venues
        except Exception as e:
            print(f"Failed to use venue agent: {e}")
            fallback = [{"name": "Mock Venue"}]
            self.memory["venue_agent_results"] = fallback
            return fallback

    def call_sponsor_agent(self, memory: dict) -> List[Any]:
        """Calls the sponsor agent passing context dict, records the output to memory, and returns it."""
        if not self.sponsor_agent or not self.extracted_info:
            print("Sponsor agent not available or missing extracted info.")
            return []
            
        try:
            print("Calling Sponsor Agent...")
            # Sponsor agent expects an event_context dict. Adapting our extracted info to it
            event_context = {
                "category": self.extracted_info.target_audience_type, # loosely mapping
                "geography": self.extracted_info.location,
                "target_audience_size": self.extracted_info.target_audience_size,
                "theme_keywords": [self.extracted_info.target_audience_type],
                "budget_min": 0,
                "budget_max": self.extracted_info.budget
            }
            
            sponsor_results_dict = self.sponsor_agent.run(
                event_context=event_context,
                memory=memory
            )
            
            sponsors = sponsor_results_dict.get("results", {}).get("top_sponsors", [])
            self.memory["sponsor_agent_results"] = sponsors
            return sponsors
        except Exception as e:
            print(f"Failed to use sponsor agent: {e}")
            fallback = [{"company_name": "Mock Sponsor"}]
            self.memory["sponsor_agent_results"] = fallback
            return fallback

    def call_pricing_agent(self, memory: dict) -> Dict[str, Any]:
        """Calls the pricing agent and records output to memory."""
        if not self.pricing_agent or not self.extracted_info:
            print("Pricing agent not available or missing extracted info.")
            return {}
            
        try:
            print("Calling Pricing Agent...")
            shared_context = {}
            if memory.get("venue_agent_results"):
                top_venue = memory["venue_agent_results"][0]
                shared_context["venue_name"] = top_venue.get('name', 'Unknown Venue') if isinstance(top_venue, dict) else getattr(top_venue, 'name', 'Unknown Venue')
                shared_context["venue_capacity"] = top_venue.get('capacity', 0) if isinstance(top_venue, dict) else getattr(top_venue, 'capacity', 0)
            
            if memory.get("sponsor_agent_results"):
                shared_context["sponsors_found"] = len(memory["sponsor_agent_results"])
                
            if memory.get("artist_agent_results"):
                shared_context["speakers_found"] = len(memory["artist_agent_results"])

            event_context = {
                "category": self.extracted_info.target_audience_type, 
                "geography": self.extracted_info.location,
                "target_audience_size": self.extracted_info.target_audience_size,
                "theme_keywords": [self.extracted_info.target_audience_type],
                "budget_min": 0.0,
                "budget_max": self.extracted_info.budget,
                "shared_context": shared_context
            }

            pricing_results_dict = self.pricing_agent.run(
                event_context=event_context,
                memory=memory
            )
            
            results = pricing_results_dict.get("results", {})
            self.memory["pricing_agent_results"] = results
            return results
        except Exception as e:
            print(f"Failed to use pricing agent: {e}")
            fallback = {"error": "Mock Pricing Result"}
            self.memory["pricing_agent_results"] = fallback
            return fallback

    def call_exhibitor_agent(self, memory: dict) -> List[Any]:
        """Calls the exhibitor agent passing context dict, records output, and returns it."""
        if not self.exhibitor_agent or not self.extracted_info or not RecommendationRequest:
            print("Exhibitor agent not available or missing extracted info.")
            return []
            
        try:
            print("Calling Exhibitor Agent...")
            request = RecommendationRequest(
                category=self.extracted_info.target_audience_type, 
                geography=self.extracted_info.location,
                audience_size=self.extracted_info.target_audience_size,
                top_n=10
            )

            # Exhibitor returns a RecommendationResponse BaseModel
            response = self.exhibitor_agent.run(request=request, memory=memory)
            exhibitors = [rec.model_dump() for rec in response.recommendations] if hasattr(response, 'recommendations') else []
            self.memory["exhibitor_agent_results"] = exhibitors
            return exhibitors
        except Exception as e:
            print(f"Failed to use exhibitor agent: {e}")
            fallback = [{"company_name": "Mock Exhibitor"}]
            self.memory["exhibitor_agent_results"] = fallback
            return fallback

    def call_community_agent(self, memory: dict) -> Dict[str, Any]:
        """Calls the community recommendation agent and records output to memory."""
        if not recommend_communities or not self.extracted_info:
            print("Community agent not available or missing extracted info.")
            return {}

        try:
            print("Calling Community Agent...")
            # Try to fetch an artist name if the artist agent found any
            artist_name = "Unknown Artist"
            if memory.get("artist_agent_results"):
                first_artist = memory["artist_agent_results"][0]
                artist_name = first_artist.get('name') if isinstance(first_artist, dict) else getattr(first_artist, 'name', 'Unknown Artist')

            input_data = {
                "event_type": "music", 
                "artist": artist_name,
                "genre": self.extracted_info.target_audience_type,
                "audience": str(self.extracted_info.target_audience_size),
                "location": self.extracted_info.location
            }
            
            community_results = recommend_communities(input_data=input_data, memory=memory)
            self.memory["community_agent_results"] = community_results
            return community_results
        except Exception as e:
            print(f"Failed to use community agent: {e}")
            fallback = {"error": "Mock Community Result"}
            self.memory["community_agent_results"] = fallback
            return fallback

    def call_instagram_agent(self, memory: dict) -> Dict[str, Any]:
        """Calls the instagram agent to build the social publishing calendar."""
        if not run_instagram_pipeline or not InstaEventDetails or not self.extracted_info:
            print("Instagram agent not available or missing extracted info.")
            return {}

        try:
            print("Calling Instagram Agent...")
            
            artist_names = []
            if memory.get("artist_agent_results"):
                for a in memory["artist_agent_results"][:3]:
                    name = a.get('name') if isinstance(a, dict) else getattr(a, 'name', 'Unknown Artist')
                    if name: artist_names.append(name)

            venue_name = self.extracted_info.location
            if memory.get("venue_agent_results"):
                top_v = memory["venue_agent_results"][0]
                venue_name = top_v.get('name') if isinstance(top_v, dict) else getattr(top_v, 'name', venue_name)

            # Build EventDetails payload exactly as the graph expects from core/models.py
            event_details = InstaEventDetails(
                name=f"{self.extracted_info.location} {self.extracted_info.target_audience_type} Event",
                date=datetime.now(), # Mock date as we don't extract it currently
                venue=venue_name,
                artists=artist_names,
                genres=[self.extracted_info.target_audience_type],
                target_audience=str(self.extracted_info.target_audience_size),
                vibe="electric, modern",
                instagram_handle="@" + self.extracted_info.location.replace(" ", "").lower() + "event"
            )

            # Execution
            final_state = run_instagram_pipeline(event_details, memory=memory)
            
            # Unpack what we care about
            calendar = final_state.get("calendar")
            posts = calendar.posts if calendar and hasattr(calendar, 'posts') else []
            
            results = {"posts_count": len(posts), "run_id": final_state.get("run_id")}
            self.memory["instagram_agent_results"] = results
            return results

        except Exception as e:
            print(f"Failed to use instagram agent: {e}")
            fallback = {"error": "Mock Instagram Result"}
            self.memory["instagram_agent_results"] = fallback
            return fallback

    def initiate_contact(self, name: str, role: str):
        """Helper to acquire contact info, send an email, and make a call."""
        contact_info = self.acquire_contact_details(name)
        print(f"Contact info for {name}: {contact_info}")
        
        email = "contact.sid.chopra@gmail.com"
        phone = "+919810706119"
        
        try:
            if email_bot and hasattr(email_bot, 'send_email'):
                email_bot.send_email(email, f"Event Inquiry - {role}", f"Hello {name}, we are interested in discussing a {role} opportunity for an upcoming event.")
            print(f"Email sent to {email}")
        except Exception as e:
            print(f"Failed to send email to {email}: {e}")
            
        try:
            if self.calling_agent and hasattr(self.calling_agent, 'make_call'):
                self.calling_agent.make_call(to=phone, script=f"Hello {name}, we want to discuss a {role} opportunity for an event.")
            print(f"Call initiated to {phone}")
        except Exception as e:
            print(f"Failed to initiate call to {phone}: {e}")

    def build_event_schedule(self, memory: dict) -> str:
        """Builds a schedule for the whole event based on current memory state."""
        if not self.extracted_info:
            return "No event details found to schedule."

        print("Building event schedule...")
        try:
            # Extract info to feed to the LLM
            artists = memory.get("artist_agent_results", [])
            venues = memory.get("venue_agent_results", [])
            
            artist_names = []
            for a in artists[:5]:
                name = a.get('name') if isinstance(a, dict) else getattr(a, 'name', 'Unknown Artist')
                if name: artist_names.append(name)
                
            venue_name = "TBD Venue"
            if venues:
                top_v = venues[0]
                venue_name = top_v.get('name') if isinstance(top_v, dict) else getattr(top_v, 'name', venue_name)
                
            prompt = f"""
            You are an expert event coordinator. Based on the following event details, create a detailed hour-by-hour schedule for the event.
            
            Event Location: {self.extracted_info.location}
            Theme/Type: {self.extracted_info.target_audience_type}
            Audience Size: {self.extracted_info.target_audience_size}
            Budget: ${self.extracted_info.budget}
            
            Selected Venue: {venue_name}
            Selected Artists/Speakers: {', '.join(artist_names) if artist_names else 'TBD'}
            
            Please provide a structured, realistic schedule.
            """
            
            response = self.llm.invoke(prompt)
            schedule = response.content if hasattr(response, 'content') else str(response)
            
            self.memory["event_schedule"] = schedule
            return schedule
        except Exception as e:
            print(f"Failed to build schedule: {e}")
            self.memory["event_schedule"] = "Schedule generation failed."
            return "Schedule generation failed."

    def execute_workflow(self, user_prompt: str):
        print(f"Processing prompt: {user_prompt}")
        
        # 1. Extract Details
        self.extracted_info = self.extract_parameters(user_prompt)
        print(f"Extracted info: {self.extracted_info}")
        
        # 2. Fetch Past Events
        relevant_events = self.fetch_previous_events(self.extracted_info.description)
        print(f"Found {len(relevant_events)} relevant past events.")
        
        # 3. Get Artists
        artist_results = self.call_artist_agent(
            location=self.extracted_info.location,
            budget=self.extracted_info.budget,
            audience_size=self.extracted_info.target_audience_size,
            memory=self.memory
        )
        
        artists_to_contact = artist_results[:3] if artist_results else []
            
        print(f"Selected artists: {artists_to_contact}")
        
        # 4. Get Venues
        venues = self.call_venue_agent(memory=self.memory)
        print(f"Selected venues: {[v.get('name', 'Unknown') if isinstance(v, dict) else v.name for v in venues]}")
        
        # 5. Get Sponsors (Adding immediately after Artists)
        sponsors = self.call_sponsor_agent(memory=self.memory)
        print(f"Selected sponsors: {[s.get('company_name', 'Unknown') for s in sponsors]}")
        
        # 6. Pricing Agent (uses venue and sponsor data)
        pricing_data = self.call_pricing_agent(memory=self.memory)
        if "revenue_projection" in pricing_data:
             print(f"Predicted total revenue: ${pricing_data['revenue_projection'].get('total_revenue', 0)}")
        
        # 7. Get Exhibitors
        exhibitors = self.call_exhibitor_agent(memory=self.memory)
        print(f"Selected exhibitors: {[e.get('name', 'Unknown') if isinstance(e, dict) else e for e in exhibitors]}")
        
        # 7. Get Communities
        communities = self.call_community_agent(memory=self.memory)
        print(f"Selected communities found: {len(communities.get('subreddits', []))} subreddits, {len(communities.get('discord_servers', []))} discord servers")

        # 8. Instagram Posts
        insta_results = self.call_instagram_agent(memory=self.memory)
        print(f"Instagram Posts Generated: {insta_results.get('posts_count', 0)} posts")

        # 9. Build Schedule
        schedule = self.build_event_schedule(memory=self.memory)
        print("Schedule generated successfully.")

        # Iterating over subset of artists to invoke calls and emails
        for artist in artists_to_contact:
            artist_name = artist.name if hasattr(artist, 'name') else (artist.get('name', 'Unknown Artist') if isinstance(artist, dict) else str(artist))
            self.initiate_contact(artist_name, "artist performance")
            
        # Iterating over top venues to invoke calls and emails
        for venue in venues[:3]:
            venue_name = venue.get('name', 'Unknown Venue') if isinstance(venue, dict) else venue.name
            self.initiate_contact(venue_name, "event venue")
            
        # Iterating over top sponsors
        for sponsor in sponsors[:3]:
            sponsor_name = sponsor.get('company_name', 'Unknown Sponsor')
            self.initiate_contact(sponsor_name, "event sponsorship")


if __name__ == "__main__":
    agent = OrchestratorAgent()
    prompt = "We are hosting an independent indie music festival in Austin, TX for about 5000 people. Looking for indie rock bands. Our budget is around $200k."
    agent.execute_workflow(prompt)
