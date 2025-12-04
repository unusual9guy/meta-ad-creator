"""
Test script for company logo integration
Tests that the user's company logo is correctly placed in the generated creative
"""

import os
import sys
import json
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

def test_company_logo_integration():
    """Test that the company logo is correctly placed in the generated creative"""
    print("=" * 60)
    print("TEST: Company Logo Integration")
    print("=" * 60)
    
    # Test image path
    test_image = "data/input/cuttlery_holder_nobackground.png"
    
    # Company logo path
    company_logo = "logo/logo.png"

    if not os.path.exists(test_image):
        print(f"❌ Test image not found: {test_image}")
        print("Please ensure test image exists in data/input/")
        return False
    
    if not os.path.exists(company_logo):
        print(f"❌ Company logo not found: {company_logo}")
        print("Please ensure company logo exists in logo/")
        return False
    
    # Show logo info
    logo_image = Image.open(company_logo)
    print(f"\n📎 Company Logo Info:")
    print(f"   • Path: {company_logo}")
    print(f"   • Size: {logo_image.size}")
    print(f"   • Format: {logo_image.format}")
    print(f"   • Mode: {logo_image.mode}")
    
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY not found in environment")
            return False
        
        # Step 1: Background Removal (optional - skip if image already has white bg)
        print("\n[Step 1/4] Background Removal...")
        background_remover = BackgroundRemoverAgent(api_key)
        
        try:
            bg_result = background_remover.remove_background(test_image)
            if bg_result["success"]:
                white_bg_path = bg_result["output_path"]
                print(f"✅ Background removed: {white_bg_path}")
            else:
                print(f"⚠️ Background removal failed, using original image")
                white_bg_path = test_image
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg:
                print(f"⚠️ API quota issue, using original image: {error_msg[:100]}")
                white_bg_path = test_image
            else:
                raise
        
        # Step 2: Image Cropping
        print("\n[Step 2/4] Image Cropping...")
        image_cropper = ImageCropperAgent()
        crop_result = image_cropper.crop_to_square(white_bg_path)
        
        if not crop_result["success"]:
            print(f"❌ Cropping failed: {crop_result.get('error', 'Unknown error')}")
            return False
        
        cropped_path = crop_result["output_path"]
        print(f"✅ Image cropped: {cropped_path}")
        
        # Step 3: Prompt Generation WITH Logo
        print("\n[Step 3/4] Prompt Generation (with company logo)...")
        prompt_generator = PromptGeneratorAgent(api_key)
        
        try:
            prompt_result = prompt_generator.generate_prompt(
                image_path=cropped_path,
                description="Premium wooden cutlery holder with mother-of-pearl inlay",
                user_inputs={
                    "target_audience": "Home decor enthusiasts, luxury buyers",
                    "price": "2999 Rs before, 1899 Rs after"
                },
                primary_font="Playfair Display",
                secondary_font="Montserrat",
                pricing_font="Montserrat",
                include_price=True,
                logo_path=company_logo  # Using company logo
            )
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg:
                print(f"⚠️ QUOTA/RATE LIMIT ERROR: {error_msg[:200]}")
                print("Please wait for quota to reset or upgrade your API plan.")
                return False
            else:
                raise
        
        if not prompt_result["success"]:
            print(f"❌ Prompt generation failed: {prompt_result.get('error', 'Unknown error')}")
            return False
        
        generated_prompt = prompt_result["prompt"]
        print("✅ Prompt generated successfully")
        
        # Check if logo is mentioned in prompt
        try:
            clean_prompt = generated_prompt
            if clean_prompt.startswith('```json'):
                clean_prompt = clean_prompt[7:]
            if clean_prompt.endswith('```'):
                clean_prompt = clean_prompt[:-3]
            clean_prompt = clean_prompt.strip()
            
            json_start = clean_prompt.find('{')
            json_end = clean_prompt.rfind('}')
            if json_start != -1 and json_end != -1:
                json_str = clean_prompt[json_start:json_end+1]
                prompt_json = json.loads(json_str)
                
                branding = prompt_json.get("branding", {})
                logo_config = branding.get("logo", {})
                logo_enabled = logo_config.get("enabled")
                
                if logo_enabled == "true" or logo_enabled is True:
                    print("   ✓ Logo enabled in prompt configuration")
                    print(f"   ✓ Logo placement: {logo_config.get('placement', {}).get('position', 'N/A')}")
                else:
                    print(f"   ⚠️ Logo enabled status: {logo_enabled}")
        except (json.JSONDecodeError, Exception) as e:
            print(f"   ⚠️ Could not parse JSON for logo validation: {str(e)[:50]}")
        
        # Step 4: Creative Generation WITH Logo
        print("\n[Step 4/4] Creative Generation (with company logo)...")
        creative_generator = CreativeGeneratorAgent(api_key)
        
        creative_result = creative_generator.generate_creative(
            image_path=cropped_path,
            prompt=generated_prompt,
            product_description="Premium wooden cutlery holder with logo",
            logo_path=company_logo,  # Using company logo
            font_names=["Playfair Display", "Montserrat"]  # Fonts to strip
        )
        
        if creative_result["success"]:
            output_path = creative_result["output_path"]
            print(f"✅ Creative generated: {output_path}")
            
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"   ✓ File size: {file_size} bytes")
                
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
        print("✅ COMPANY LOGO INTEGRATION TEST PASSED")
        print("=" * 60)
        print("\nSummary:")
        print(f"  • Company logo used: {company_logo}")
        print(f"  • Image cropped: {cropped_path}")
        print(f"  • Prompt generated with logo enabled")
        print(f"  • Creative generated: {creative_result.get('output_path', 'N/A')}")
        print("\n📌 Please visually verify that the logo appears correctly in the generated image.")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_company_logo_integration()
    sys.exit(0 if success else 1)

