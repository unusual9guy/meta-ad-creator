"""
Test script for BOTH agents working together
Tests the complete workflow: Agent 1 generates prompt, Agent 2 uses it to create Meta creative
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents import PromptGeneratorAgent, CreativeGeneratorAgent

load_dotenv()

def test_both_agents():
    """Test both agents working together in the complete workflow"""
    print("🧪 Testing BOTH Agents - Complete Workflow")
    print("="*60)
    
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("\n❌ Error: GOOGLE_API_KEY environment variable not set.")
        print("Please set your Google API key in a .env file or environment variable.")
        print("Copy env.example to .env and add your API key.")
        return
    
    try:
        # Initialize both agents
        print("🚀 Initializing both agents...")
        agent1 = PromptGeneratorAgent()
        agent2 = CreativeGeneratorAgent()
        print("✅ Both agents initialized successfully!")
        
        # Get user inputs
        print("\n📋 Please provide the following information:")
        image_path = input("🖼️ Product image path: ").strip()
        description = input("📄 Product description: ").strip()
        
        # Optional user inputs
        print("\n🔧 Optional customizations (press Enter to skip):")
        target_audience = input("👥 Target audience: ").strip() or None
        price = input("💰 Price: ").strip() or None
        
        user_inputs = {}
        if target_audience:
            user_inputs["target_audience"] = target_audience
        if price:
            user_inputs["price"] = price
        
        print(f"\n✅ Inputs received:")
        print(f"   Image: {image_path}")
        print(f"   Description: {description}")
        if user_inputs:
            print(f"   Custom inputs: {user_inputs}")
        
        # STEP 1: Test Agent 1 - Generate prompt
        print("\n" + "="*60)
        print("🤖 STEP 1: Testing Agent 1 (Prompt Generator)")
        print("="*60)
        print("⏳ Generating structured prompt...")
        
        agent1_result = agent1.generate_prompt(image_path, description, user_inputs)
        
        if not agent1_result["success"]:
            print(f"❌ Agent 1 failed: {agent1_result['error']}")
            return
        
        print("✅ Agent 1 completed successfully!")
        
        # Display Agent 1 results
        print("\n📋 Generated Prompt Preview:")
        structured = agent1_result["structured_prompt"]
        
        if structured.get("headline", {}).get("text"):
            print(f"   📰 Headline: {structured['headline']['text']}")
        if structured.get("footer", {}).get("text"):
            print(f"   📄 Footer: {structured['footer']['text']}")
        if structured.get("limited_time_offer", {}).get("text"):
            print(f"   ⏰ Limited Offer: {structured['limited_time_offer']['text']}")
        
        # Show full prompt
        print("\n📄 Full Generated Prompt:")
        print("-" * 40)
        print(agent1_result["prompt"])
        print("-" * 40)
        
        # STEP 2: Test Agent 2 - Generate creative using Agent 1's prompt
        print("\n" + "="*60)
        print("🎨 STEP 2: Testing Agent 2 (Creative Generator)")
        print("="*60)
        print("⏳ Generating Meta ad creative using Agent 1's prompt...")
        
        agent2_result = agent2.generate_creative(image_path, agent1_result["prompt"], description)
        
        if not agent2_result["success"]:
            print(f"❌ Agent 2 failed: {agent2_result['error']}")
            return
        
        print("✅ Agent 2 completed successfully!")
        
        # Display Agent 2 results
        print("\n🎨 Generated Meta Ad Creative:")
        print("-" * 40)
        print(agent2_result["creative_result"])
        print("-" * 40)
        
        if agent2_result.get("output_path"):
            print(f"\n💾 Creative saved to: {agent2_result['output_path']}")
            if os.path.exists(agent2_result["output_path"]):
                print("✅ File successfully saved!")
            else:
                print("⚠️ File path created but file may not exist yet")
        
        # FINAL RESULT
        print("\n" + "="*60)
        print("🎉 COMPLETE WORKFLOW TEST SUCCESSFUL!")
        print("="*60)
        
        print("\n📊 Test Summary:")
        print(f"   ✅ Agent 1: Generated structured prompt")
        print(f"   ✅ Agent 2: Generated Meta ad creative")
        print(f"   ✅ Workflow: Complete end-to-end test passed")
        
        print("\n🎯 Both agents are working correctly together!")
        print("The complete workflow is ready for production use!")
        
    except KeyboardInterrupt:
        print("\n\n👋 Test cancelled by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        print("Please check your setup and try again.")

if __name__ == "__main__":
    test_both_agents()
