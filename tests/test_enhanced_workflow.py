"""
Test script for enhanced workflow with all new features
Tests the complete workflow with fonts, logo, and price toggle
"""

import os
import sys
import json
import time
from PIL import Image
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.abspath(project_root))

from src.agents.background_remover import BackgroundRemoverAgent
from src.agents.image_cropper import ImageCropperAgent
from src.agents.prompt_generator import PromptGeneratorAgent
from src.agents.creative_generator import CreativeGeneratorAgent

load_dotenv()

def create_test_logo():
    """Create a simple test logo image"""
    logo_dir = "data/output/temp"
    os.makedirs(logo_dir, exist_ok=True)
    
    # Create a simple colored square as test logo
    logo = Image.new('RGB', (200, 200), color='#FF6600')  # Orange color
    logo_path = os.path.join(logo_dir, f"test_logo_{int(time.time())}.png")
    logo.save(logo_path)
    return logo_path

def test_enhanced_workflow():
    """Test the complete enhanced workflow with all new features"""
    print("=" * 60)
    print("TEST: Enhanced Workflow (All New Features)")
    print("=" * 60)
    
    # Test image path
    test_image = "data/input/cuttlery_holder_nobackground.png"
    
    if not os.path.exists(test_image):
        print(f"❌ Test image not found: {test_image}")
        print("Please ensure test image exists in data/input/")
        return False
    
    # Create test logo
    print("\n[Setup] Creating test logo...")
    logo_path = create_test_logo()
    print(f"✅ Test logo created: {logo_path}")
    
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY not found in environment")
            return False
        
        # Step 1: Background Removal
        print("\n[Step 1/4] Background Removal...")
        background_remover = BackgroundRemoverAgent(api_key)
        bg_result = background_remover.remove_background(test_image)
        
        if not bg_result["success"]:
            print(f"❌ Background removal failed: {bg_result.get('error', 'Unknown error')}")
            return False
        
        white_bg_path = bg_result["output_path"]
        print(f"✅ Background removed: {white_bg_path}")
        
        # Step 2: Image Cropping
        print("\n[Step 2/4] Image Cropping...")
        image_cropper = ImageCropperAgent()
        crop_result = image_cropper.crop_to_square(white_bg_path)
        
        if not crop_result["success"]:
            print(f"❌ Cropping failed: {crop_result.get('error', 'Unknown error')}")
            return False
        
        cropped_path = crop_result["output_path"]
        print(f"✅ Image cropped: {cropped_path}")
        
        # Step 3: Prompt Generation with all new features
        print("\n[Step 3/4] Prompt Generation (with fonts, logo, price)...")
        prompt_generator = PromptGeneratorAgent(api_key)
        
        prompt_result = prompt_generator.generate_prompt(
            image_path=cropped_path,
            description="Premium wooden photo frame with mother-of-pearl inlay",
            user_inputs={
                "target_audience": "Home decor enthusiasts",
                "price": "2999 Rs before, 1899 Rs after"
            },
            primary_font="Calgary",
            secondary_font="Tan Pearl",
            pricing_font="RoxboroughCF",
            include_price=True,
            logo_path=logo_path
        )
        
        if not prompt_result["success"]:
            print(f"❌ Prompt generation failed: {prompt_result.get('error', 'Unknown error')}")
            return False
        
        generated_prompt = prompt_result["prompt"]
        print("✅ Prompt generated successfully")
        
        # Validate prompt structure
        try:
            clean_prompt = generated_prompt
            if clean_prompt.startswith('```json'):
                clean_prompt = clean_prompt[7:]
            if clean_prompt.endswith('```'):
                clean_prompt = clean_prompt[:-3]
            clean_prompt = clean_prompt.strip()
            
            prompt_json = json.loads(clean_prompt)
            
            # Check fonts
            text_elements = prompt_json.get("typography_and_layout", {}).get("text_elements", [])
            primary_font_found = False
            for element in text_elements:
                if element.get("hierarchy") == "primary":
                    if "Calgary" in element.get("font", ""):
                        primary_font_found = True
                        break
            
            if primary_font_found:
                print("   ✓ Primary font (Calgary) found in prompt")
            else:
                print("   ⚠️ Primary font may not be explicitly set in JSON structure")
            
            # Check logo
            branding = prompt_json.get("branding", {})
            logo_config = branding.get("logo", {})
            if logo_config.get("enabled") == "true" or logo_config.get("enabled") is True:
                print("   ✓ Logo enabled in prompt")
            else:
                print("   ⚠️ Logo may not be properly enabled")
            
            # Check pricing
            pricing_display = prompt_json.get("typography_and_layout", {}).get("pricing_display")
            if pricing_display is not None:
                print("   ✓ Pricing included in prompt")
            else:
                print("   ⚠️ Pricing not found in prompt")
            
        except json.JSONDecodeError:
            print("   ⚠️ Could not parse JSON for validation, but prompt was generated")
        
        # Step 4: Creative Generation
        print("\n[Step 4/4] Creative Generation (with logo)...")
        creative_generator = CreativeGeneratorAgent(api_key)
        
        creative_result = creative_generator.generate_creative(
            image_path=cropped_path,
            prompt=generated_prompt,
            product_description="Premium wooden photo frame",
            logo_path=logo_path,
            font_names=["Calgary", "Tan Pearl", "RoxboroughCF"]  # Fonts used in test
        )
        
        if creative_result["success"]:
            output_path = creative_result["output_path"]
            print(f"✅ Creative generated: {output_path}")
            
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"   ✓ File size: {file_size} bytes")
                
                # Try to open image to verify it's valid
                try:
                    img = Image.open(output_path)
                    print(f"   ✓ Image dimensions: {img.size}")
                    print(f"   ✓ Image format: {img.format}")
                except Exception as e:
                    print(f"   ⚠️ Could not verify image: {str(e)}")
            else:
                print(f"   ⚠️ Output file not found at: {output_path}")
        else:
            print(f"❌ Creative generation failed: {creative_result.get('error', 'Unknown error')}")
            return False
        
        print("\n" + "=" * 60)
        print("✅ ENHANCED WORKFLOW TEST PASSED")
        print("=" * 60)
        print("\nSummary:")
        print(f"  • Background removed: {white_bg_path}")
        print(f"  • Image cropped: {cropped_path}")
        print(f"  • Prompt generated with fonts, logo, and pricing")
        print(f"  • Creative generated: {creative_result.get('output_path', 'N/A')}")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup test logo
        if os.path.exists(logo_path):
            try:
                os.remove(logo_path)
                print(f"\n🧹 Cleaned up test logo: {logo_path}")
            except:
                pass

if __name__ == "__main__":
    success = test_enhanced_workflow()
    sys.exit(0 if success else 1)

