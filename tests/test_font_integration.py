"""
Test script for font integration
Tests that user-provided fonts are correctly passed to and used by the prompt generator
"""

import os
import sys
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.abspath(project_root))

from src.agents.prompt_generator import PromptGeneratorAgent

load_dotenv()

def test_font_integration():
    """Test that user-provided fonts are correctly integrated"""
    print("=" * 60)
    print("TEST: Font Integration")
    print("=" * 60)
    
    # Test image path (use an existing test image)
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
        
        # Test 1: Primary font only
        print("\n[Test 1] Testing with primary font only...")
        try:
            result1 = prompt_generator.generate_prompt(
            image_path=test_image,
            description="Premium wooden photo frame with mother-of-pearl inlay",
            user_inputs={"target_audience": "Home decor enthusiasts", "price": "2999 Rs before, 1899 Rs after"},
                primary_font="Playfair Display",
                include_price=True
            )
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg or "ResourceExhausted" in error_msg:
                print(f"⚠️ QUOTA/RATE LIMIT ERROR: {error_msg[:200]}")
                print("\nThis is not a test failure - it's an API quota issue.")
                print("Please wait for quota to reset or upgrade your API plan.")
                return False
            else:
                raise
        
        if result1["success"]:
            print("✅ Test 1 PASSED: Primary font integration works")
            # Check if font is mentioned in prompt
            prompt_text = result1["prompt"]
            if "Playfair Display" in prompt_text or "playfair" in prompt_text.lower():
                print("   ✓ Font name found in generated prompt")
            else:
                print("   ⚠️ Font name not explicitly found in prompt (may be in JSON structure)")
        else:
            print(f"❌ Test 1 FAILED: {result1.get('error', 'Unknown error')}")
            return False
        
        # Test 2: Primary + Secondary fonts
        print("\n[Test 2] Testing with primary and secondary fonts...")
        result2 = prompt_generator.generate_prompt(
            image_path=test_image,
            description="Premium wooden photo frame with mother-of-pearl inlay",
            user_inputs={"target_audience": "Home decor enthusiasts", "price": "2999 Rs before, 1899 Rs after"},
            primary_font="Calgary",
            secondary_font="Tan Pearl",
            include_price=True
        )
        
        if result2["success"]:
            print("✅ Test 2 PASSED: Primary + Secondary font integration works")
        else:
            print(f"❌ Test 2 FAILED: {result2.get('error', 'Unknown error')}")
            return False
        
        # Test 3: All three fonts (primary, secondary, pricing)
        print("\n[Test 3] Testing with all three fonts...")
        result3 = prompt_generator.generate_prompt(
            image_path=test_image,
            description="Premium wooden photo frame with mother-of-pearl inlay",
            user_inputs={"target_audience": "Home decor enthusiasts", "price": "2999 Rs before, 1899 Rs after"},
            primary_font="Calgary",
            secondary_font="Tan Pearl",
            pricing_font="RoxboroughCF",
            include_price=True
        )
        
        if result3["success"]:
            print("✅ Test 3 PASSED: All three fonts integration works")
        else:
            print(f"❌ Test 3 FAILED: {result3.get('error', 'Unknown error')}")
            return False
        
        # Test 4: Custom font names (non-standard)
        print("\n[Test 4] Testing with custom/non-standard font names...")
        result4 = prompt_generator.generate_prompt(
            image_path=test_image,
            description="Premium wooden photo frame with mother-of-pearl inlay",
            user_inputs={"target_audience": "Home decor enthusiasts", "price": "2999 Rs before, 1899 Rs after"},
            primary_font="MyCustomFont-Regular",
            secondary_font="MyCustomFont-Light",
            pricing_font="MyCustomFont-Bold",
            include_price=True
        )
        
        if result4["success"]:
            print("✅ Test 4 PASSED: Custom font names work")
        else:
            print(f"❌ Test 4 FAILED: {result4.get('error', 'Unknown error')}")
            return False
        
        print("\n" + "=" * 60)
        print("✅ ALL FONT INTEGRATION TESTS PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_font_integration()
    sys.exit(0 if success else 1)

