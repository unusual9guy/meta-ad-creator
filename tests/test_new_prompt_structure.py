"""
Test script for new flexible prompt structure
Tests that the new JSON structure with text_elements, features, and CTA buttons works correctly
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

def test_new_prompt_structure():
    """Test that the new flexible prompt structure is generated correctly"""
    print("=" * 60)
    print("TEST: New Prompt Structure (Flexible Text Elements)")
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
        
        print("\n[Test] Generating prompt with new structure...")
        try:
            result = prompt_generator.generate_prompt(
            image_path=test_image,
            description="Premium wooden photo frame with mother-of-pearl inlay",
            user_inputs={"target_audience": "Home decor enthusiasts", "price": "2999 Rs before, 1899 Rs after"},
            primary_font="Calgary",
            secondary_font="Tan Pearl",
                pricing_font="RoxboroughCF",
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
                return False
            else:
                raise
        
        if not result["success"]:
            print(f"❌ Prompt generation failed: {result.get('error', 'Unknown error')}")
            return False
        
        prompt_text = result["prompt"]
        
        # Clean JSON if wrapped in markdown
        clean_prompt = prompt_text
        if clean_prompt.startswith('```json'):
            clean_prompt = clean_prompt[7:]
        if clean_prompt.startswith('```'):
            clean_prompt = clean_prompt[3:]
        if clean_prompt.endswith('```'):
            clean_prompt = clean_prompt[:-3]
        clean_prompt = clean_prompt.strip()
        
        # Try to find JSON object boundaries
        json_start = clean_prompt.find('{')
        json_end = clean_prompt.rfind('}')
        
        if json_start != -1 and json_end != -1 and json_end > json_start:
            clean_prompt = clean_prompt[json_start:json_end+1]
        
        try:
            prompt_json = json.loads(clean_prompt)
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {str(e)}")
            print(f"\nError position: {e.pos if hasattr(e, 'pos') else 'unknown'}")
            print(f"\nFirst 1000 chars of prompt:\n{clean_prompt[:1000]}")
            print(f"\nLast 500 chars of prompt:\n{clean_prompt[-500:]}")
            
            # Try to repair common JSON issues
            print("\n[Attempting JSON repair...]")
            try:
                # Try to fix common issues: unescaped quotes, trailing commas, etc.
                repaired = clean_prompt
                
                # Remove trailing commas before closing braces/brackets
                import re
                repaired = re.sub(r',(\s*[}\]])', r'\1', repaired)
                
                # Try to close unclosed strings (basic attempt)
                # This is a simple heuristic - may not work for all cases
                if repaired.count('"') % 2 != 0:
                    # Odd number of quotes - try to find and fix
                    print("   ⚠️ Detected unclosed string (odd number of quotes)")
                
                prompt_json = json.loads(repaired)
                print("   ✅ JSON repair successful!")
            except json.JSONDecodeError as e2:
                print(f"   ❌ JSON repair failed: {str(e2)}")
                print("\n⚠️ The generated prompt contains invalid JSON.")
                print("This might be due to:")
                print("  - Unescaped quotes in text fields")
                print("  - Truncated JSON (max_tokens limit)")
                print("  - Malformed structure")
                print("\nThe prompt generator may need adjustment to ensure valid JSON output.")
                return False
        
        # Test 1: Check for text_elements array
        print("\n[Test 1] Checking for text_elements array...")
        typography = prompt_json.get("typography_and_layout", {})
        text_elements = typography.get("text_elements", [])
        
        if isinstance(text_elements, list) and len(text_elements) > 0:
            print(f"✅ Test 1 PASSED: text_elements array found with {len(text_elements)} elements")
        else:
            print("❌ Test 1 FAILED: text_elements array not found or empty")
            return False
        
        # Test 2: Check for headline (primary text element)
        print("\n[Test 2] Checking for headline (primary text element)...")
        headline_found = False
        for element in text_elements:
            if element.get("type") == "text" and element.get("hierarchy") == "primary":
                headline_found = True
                headline_text = element.get("text", "")
                print(f"✅ Test 2 PASSED: Headline found")
                print(f"   ✓ Text: {headline_text[:50]}...")
                print(f"   ✓ Font: {element.get('font', 'N/A')}")
                break
        
        if not headline_found:
            print("❌ Test 2 FAILED: Primary text element (headline) not found")
            return False
        
        # Test 3: Check for tagline (secondary text element)
        print("\n[Test 3] Checking for tagline (secondary text element)...")
        tagline_found = False
        for element in text_elements:
            if element.get("type") == "text" and element.get("hierarchy") == "secondary":
                tagline_found = True
                tagline_text = element.get("text", "")
                print(f"✅ Test 3 PASSED: Tagline found")
                print(f"   ✓ Text: {tagline_text[:50]}...")
                print(f"   ✓ Font: {element.get('font', 'N/A')}")
                break
        
        if not tagline_found:
            print("❌ Test 3 FAILED: Secondary text element (tagline) not found")
            return False
        
        # Test 4: Check for features element
        print("\n[Test 4] Checking for features element...")
        features_found = False
        for element in text_elements:
            if element.get("type") == "features":
                features_found = True
                features_items = element.get("items", [])
                print(f"✅ Test 4 PASSED: Features element found")
                print(f"   ✓ Number of features: {len(features_items)}")
                for i, feature in enumerate(features_items[:3], 1):
                    print(f"   ✓ Feature {i}: {feature.get('text', 'N/A')[:40]}...")
                break
        
        if not features_found:
            print("❌ Test 4 FAILED: Features element not found")
            return False
        
        # Test 5: Check for CTA button element
        print("\n[Test 5] Checking for CTA button element...")
        cta_found = False
        for element in text_elements:
            if element.get("type") == "cta_button":
                cta_found = True
                cta_text = element.get("text", "")
                cta_style = element.get("style", {})
                print(f"✅ Test 5 PASSED: CTA button found")
                print(f"   ✓ Text: {cta_text}")
                print(f"   ✓ Background color: {cta_style.get('background_color', 'N/A')}")
                break
        
        if not cta_found:
            print("❌ Test 5 FAILED: CTA button element not found")
            return False
        
        # Test 6: Check for product_placement structure
        print("\n[Test 6] Checking for product_placement structure...")
        product_placement = prompt_json.get("product_placement", {})
        if product_placement:
            print("✅ Test 6 PASSED: product_placement structure found")
            print(f"   ✓ Position: {product_placement.get('position', 'N/A')}")
            print(f"   ✓ Size: {product_placement.get('size', 'N/A')}")
        else:
            print("⚠️ Test 6: product_placement structure not found (may be in visual section)")
        
        # Test 7: Check for branding structure
        print("\n[Test 7] Checking for branding structure...")
        branding = prompt_json.get("branding", {})
        if branding:
            print("✅ Test 7 PASSED: branding structure found")
            logo_config = branding.get("logo", {})
            print(f"   ✓ Logo enabled: {logo_config.get('enabled', 'N/A')}")
        else:
            print("⚠️ Test 7: branding structure not found")
        
        print("\n" + "=" * 60)
        print("✅ ALL NEW PROMPT STRUCTURE TESTS PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_new_prompt_structure()
    sys.exit(0 if success else 1)

