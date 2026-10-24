"""
Interactive CLI Console for Cold Chain Logistics AI Agent.
Runs directly in your PowerShell / Command Prompt terminal with zero UI lag or black screens.
"""
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_core.messages import HumanMessage, AIMessage
from src.agent.graph import create_agent

def main():
    print("=" * 70)
    print("❄️  COLD CHAIN LOGISTICS AI - TERMINAL CONSOLE")
    print("   PostgreSQL (32,065 rows) • Pinecone RAG • Open-Meteo • Claude")
    print("=" * 70)
    print("Commands:")
    print(" - Type your operational inquiry or record ID check")
    print(" - Type 'sample' to run a test on Record ID 3727 (Temp Breach)")
    print(" - Type 'exit' or 'quit' to close")
    print("-" * 70)

    print("\n[INFO] Initializing LangGraph agent...")
    agent = create_agent()
    print("[READY] Agent online! You can start asking questions.\n")

    history = []

    while True:
        try:
            user_input = input("\n👤 Dispatcher > ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q"]:
                print("Exiting console. Goodbye!")
                break

            if user_input.lower() == "sample":
                user_input = "Check telemetry for Record ID 3727. What is the current cargo temperature, and what immediate actions does SOP v2.4 require?"
                print(f"Running sample query:\n\"{user_input}\"")

            history.append(HumanMessage(content=user_input))
            print("\n🤖 AI Agent thinking (checking DB, Pinecone SOPs, and weather)...")

            result = agent.invoke({"messages": history})
            last_message = result["messages"][-1]
            response_text = last_message.content

            print("\n" + "=" * 70)
            print("📋 AGENT OPERATIONAL RESPONSE:")
            print("=" * 70)
            print(response_text)
            print("=" * 70)

            history.append(AIMessage(content=response_text))

        except KeyboardInterrupt:
            print("\nSession interrupted. Exiting.")
            break
        except Exception as e:
            print(f"\n[ERROR] An error occurred: {e}")

if __name__ == "__main__":
    main()

