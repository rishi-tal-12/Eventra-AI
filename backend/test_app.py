import os
import sys

# Ensure the project root is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.orchestrator_agent import OrchestratorAgent

def test_orchestrator():
    print("Initializing Orchestrator Agent...")
    try:
        agent = OrchestratorAgent()
    except Exception as e:
        print(f"Failed to initialize OrchestratorAgent: {e}")
        return

    # Sample prompt covering location, audience, size, and domain (genres/budget implicitly)
    sample_prompt = (
        "We are planning a massive EDM music and technology festival in Miami, Florida "
        "for around 10,000 attendees this winter. We need top-tier DJs, modern "
        "large-capacity venues, and tech sponsors. Our overall budget is $500,000."
    )
    
    print("-" * 50)
    print(f"Running workflow with prompt:\n'{sample_prompt}'")
    print("-" * 50 + "\n")
    
    # execute_workflow internally calls all individual component functions:
    # (parsing, past events, artists, venues, sponsors, communities, pricing, instagram, exhibitors, etc.)
    try:
        agent.execute_workflow(sample_prompt)
        print("\nWorkflow execution completed successfully!")
        
        print("\nFinal Memory State Keys Populated:")
        for key, val in agent.memory.items():
            status = "Populated" if val else "Empty/Failed"
            print(f"- {key}: {status}")

    except Exception as e:
        print(f"\nError during workflow execution: {e}")

if __name__ == "__main__":
    test_orchestrator()