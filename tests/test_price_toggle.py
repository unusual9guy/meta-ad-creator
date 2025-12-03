"""
Test script for price toggle integration
Tests that pricing can be included or excluded from the prompt
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.abspath(project_root))

from src.agents.prompt_generator import PromptGeneratorAgent

load_dotenv()

def test_price_toggle():
    """Test that price toggle works correctly"""
    print("=" * 60)
    print("TEST: Price Toggle Integration")
    print("=" * 60)
    
    # Test image path
    test_image = "data/input/cuttlery_holder_nobackground.png"
    
    if not os.path.exists(test_image):
        print(f"❌ Test image not found: {test_image}")
        print("Please ensure test image exists in data/input/")
        return False
    
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY not found in environment")
            return False
        
        prompt_generator = PromptGeneratorAgent(api_key)
        
        # Test 1: Price included
        print("\n[Test 1] Testing with price INCLUDED...")
        try:
            result1 = prompt_generator.generate_prompt(
            image_path=test_image,
            description="Premium wooden photo frame with mother-of-pearl inlay",
            user_inputs={"target_audience": "Home decor enthusiasts", "price": "2999 Rs before, 1899 Rs after"},
                primary_font="Calgary",
                include_price=True
            )
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg or "ResourceExhausted" in error_msg:
                print(f"⚠️ QUOTA/RATE LIMIT ERROR: {error_msg[:200]}")
                print("\nThis is not a test failure - it's an API quota issue.")
                print("Possible solutions:")
                print("  1. Wait for quota to reset (check the retry_delay in the error)")
                print("  2. Upgrade your Google API plan")
                print("  3. Check if gemini-2.5-flash-image-preview is available on your tier")
                print("  4. Use a different API key with available quota")
                return False
            else:
                raise  # Re-raise if it's a different error
        
        if result1["success"]:
            prompt_text = result1["prompt"]
            # Try to parse JSON to check structure
            try:
                # Clean JSON if wrapped in markdown
                clean_prompt = prompt_text
                if clean_prompt.startswith('```json'):
                    clean_prompt = clean_prompt[7:]
                if clean_prompt.endswith('```'):
                    clean_prompt = clean_prompt[:-3]
                clean_prompt = clean_prompt.strip()
                
                prompt_json = json.loads(clean_prompt)
                pricing_display = prompt_json.get("typography_and_layout", {}).get("pricing_display")
                limited_offer = prompt_json.get("typography_and_layout", {}).get("limited_time_offer")
                
                if pricing_display is not None and limited_offer is not None:
                    print("✅ Test 1 PASSED: Price is included in prompt")
                    print(f"   ✓ Pricing display: {pricing_display is not None}")
                    print(f"   ✓ Limited offer: {limited_offer is not None}")
                else:
                    print("❌ Test 1 FAILED: Price elements not found in prompt JSON")
                    return False
            except json.JSONDecodeError as e:
                print(f"⚠️ Could not parse JSON, but prompt generated: {str(e)}")
                # Check if price-related text is in prompt
                if "price" in prompt_text.lower() or "pricing" in prompt_text.lower():
                    print("✅ Test 1 PASSED: Price-related text found in prompt")
                else:
                    print("❌ Test 1 FAILED: No price-related text found")
                    return False
        else:
            print(f"❌ Test 1 FAILED: {result1.get('error', 'Unknown error')}")
            return False
        
        # Test 2: Price excluded
        print("\n[Test 2] Testing with price EXCLUDED...")
        result2 = prompt_generator.generate_prompt(
            image_path=test_image,
            description="Premium wooden photo frame with mother-of-pearl inlay",
            user_inputs={"target_audience": "Home decor enthusiasts"},
            primary_font="Calgary",
            include_price=False
        )
        
        if result2["success"]:
            prompt_text = result2["prompt"]
            # Try to parse JSON to check structure
            try:
                # Clean JSON if wrapped in markdown
                clean_prompt = prompt_text
                if clean_prompt.startswith('```json'):
                    clean_prompt = clean_prompt[7:]
                if clean_prompt.endswith('```'):
                    clean_prompt = clean_prompt[:-3]
                clean_prompt = clean_prompt.strip()
                
                prompt_json = json.loads(clean_prompt)
                pricing_display = prompt_json.get("typography_and_layout", {}).get("pricing_display")
                limited_offer = prompt_json.get("typography_and_layout", {}).get("limited_time_offer")
                
                if pricing_display is None and limited_offer is None:
                    print("✅ Test 2 PASSED: Price is excluded from prompt")
                    print("   ✓ Pricing display: null")
                    print("   ✓ Limited offer: null")
                else:
                    print("❌ Test 2 FAILED: Price elements still present when excluded")
                    print(f"   Pricing display: {pricing_display}")
                    print(f"   Limited offer: {limited_offer}")
                    return False
            except json.JSONDecodeError as e:
                print(f"⚠️ Could not parse JSON, but prompt generated: {str(e)}")
                # Check if price-related text is minimal in prompt
                price_mentions = prompt_text.lower().count("price")
                if price_mentions < 3:  # Should have minimal price mentions
                    print("✅ Test 2 PASSED: Minimal price mentions in prompt")
                else:
                    print(f"❌ Test 2 FAILED: Too many price mentions ({price_mentions})")
                    return False
        else:
            print(f"❌ Test 2 FAILED: {result2.get('error', 'Unknown error')}")
            return False
        
        print("\n" + "=" * 60)
        print("✅ ALL PRICE TOGGLE TESTS PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_price_toggle()
    sys.exit(0 if success else 1)

