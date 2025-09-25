"""
Test script for Agent 1 (Prompt Generator) only
Tests the prompt generation with sample data
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agent1_prompt_generator import PromptGeneratorAgent

load_dotenv()

def test_agent1():
    """Test Agent 1 with sample data"""
    print("🧪 Testing Agent 1 (Prompt Generator)")
    print("="*50)
    
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("\n❌ Error: GOOGLE_API_KEY environment variable not set.")
        print("Please set your Google API key in a .env file or environment variable.")
        print("Copy env.example to .env and add your API key.")
        return
    
    try:
        # Initialize Agent 1
        print("🚀 Initializing Agent 1...")
        agent1 = PromptGeneratorAgent()
        print("✅ Agent 1 initialized successfully!")
        
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
        
        # Test Agent 1
        print("\n🔍 Testing Agent 1 prompt generation...")
        print("⏳ This may take a moment as it processes the image...")
        
        result = agent1.generate_prompt(
            image_path,
            description,
            user_inputs
        )
        
        if result["success"]:
            print("\n✅ Agent 1 test successful!")
            
            # Display the generated prompt
            print("\n" + "="*60)
            print("📝 GENERATED JSON PROMPT")
            print("="*60)
            print(result["prompt"])
            
            # Extract and review headline and footer
            print("\n" + "="*60)
            print("🔍 REVIEWING GENERATED CONTENT")
            print("="*60)
            
            # Try to extract headline and footer from the JSON
            import json
            try:
                # Check if JSON is complete
                if not result["prompt"].strip().endswith('}'):
                    print("⚠️ Warning: JSON appears to be incomplete. Attempting to fix...")
                    # Try to add missing closing brace
                    fixed_prompt = result["prompt"].strip()
                    if not fixed_prompt.endswith('}'):
                        fixed_prompt += '}'
                    result["prompt"] = fixed_prompt
                
                prompt_json = json.loads(result["prompt"])
                headline = prompt_json.get("typography_and_layout", {}).get("headline", {}).get("text", "")
                footer = prompt_json.get("typography_and_layout", {}).get("footer", {}).get("text", "")
                limited_offer = prompt_json.get("typography_and_layout", {}).get("limited_time_offer", {}).get("text", "")
                
                if headline:
                    print(f"\n📰 Generated Headline: '{headline}'")
                if footer:
                    print(f"\n📄 Generated Footer: '{footer}'")
                if limited_offer:
                    print(f"\n⏰ Generated Limited Offer: '{limited_offer}'")
                
                # Ask user to review
                print("\n🤔 Do you want to keep these generated texts?")
                print("   [y] Yes, proceed with these")
                print("   [n] No, let me provide custom ones")
                
                while True:
                    choice = input("\nEnter your choice (y/n): ").lower().strip()
                    if choice in ['y', 'yes']:
                        print("✅ Proceeding with generated content!")
                        break
                    elif choice in ['n', 'no']:
                        # Get custom inputs
                        custom_headline = input("📰 Enter your custom headline: ").strip()
                        custom_footer = input("📄 Enter your custom footer: ").strip()
                        custom_offer = input("⏰ Enter your custom limited offer: ").strip()
                        
                        if custom_headline or custom_footer or custom_offer:
                            print("✅ Custom content received!")
                            # Update the JSON with custom content
                            if custom_headline:
                                prompt_json["typography_and_layout"]["headline"]["text"] = custom_headline
                            if custom_footer:
                                prompt_json["typography_and_layout"]["footer"]["text"] = custom_footer
                            if custom_offer:
                                prompt_json["typography_and_layout"]["limited_time_offer"]["text"] = custom_offer
                            
                            # Update the result
                            result["prompt"] = json.dumps(prompt_json, indent=2)
                            print("\n📝 Updated prompt with custom content!")
                        break
                    else:
                        print("❌ Invalid choice. Please enter y or n.")
                        
            except json.JSONDecodeError:
                print("⚠️ Could not parse JSON prompt for review.")
                print("📝 Raw prompt output:")
                print(result["prompt"])
            
            # Ask if user wants to see the final prompt
            print("\n" + "="*60)
            show_final = input("🤔 Do you want to see the final prompt? (y/n): ").lower().strip()
            if show_final in ['y', 'yes']:
                print("\n" + "="*60)
                print("📄 FINAL PROMPT")
                print("="*60)
                print(result["prompt"])
            
            print("\n✅ Agent 1 test completed successfully!")
            print("🎯 The prompt generation is working correctly!")
            
        else:
            print(f"\n❌ Agent 1 test failed: {result['error']}")
            print("Please check your API key and try again.")
            
    except KeyboardInterrupt:
        print("\n\n👋 Test cancelled by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        print("Please check your setup and try again.")

if __name__ == "__main__":
    test_agent1()
