"""
Test script for Image Cropper Agent
Tests cropping multiple images to 1:1 ratio
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents import ImageCropperAgent

load_dotenv()

def test_single_image():
    """Test cropping a single image"""
    print("🧪 Testing Single Image Cropping")
    print("="*50)
    
    try:
        # Initialize agent
        cropper = ImageCropperAgent()
        print("✅ Image Cropper Agent initialized!")
        
        # Get image path
        image_path = input("🖼️ Enter image path: ").strip()
        
        if not os.path.exists(image_path):
            print(f"❌ Image not found: {image_path}")
            return
        
        print(f"📁 Processing: {image_path}")
        
        # Crop the image
        result = cropper.crop_to_square(image_path)
        
        if result["success"]:
            print("✅ Image cropped successfully!")
            print(f"📏 Original dimensions: {result['original_dimensions']}")
            print(f"📏 Cropped dimensions: {result['cropped_dimensions']}")
            print(f"💾 Output saved to: {result['output_path']}")
            
            if result.get("crop_applied"):
                if "product_bounds" in result:
                    print("🧠 Intelligent cropping applied:")
                    print(f"   🎯 Product detected at: {result['product_bounds']}")
                    print(f"   📐 Crop area: {result['crop_area']}")
                    print("   ✨ Auto-centered and sized for optimal composition")
                else:
                    print(f"✂️ Basic crop coordinates: {result.get('crop_coordinates', 'N/A')}")
            else:
                print("ℹ️ No cropping needed - image was already square")
        else:
            print(f"❌ Cropping failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_multiple_images():
    """Test cropping multiple images"""
    print("\n🧪 Testing Multiple Image Cropping")
    print("="*50)
    
    try:
        # Initialize agent
        cropper = ImageCropperAgent()
        print("✅ Image Cropper Agent initialized!")
        
        # Get image paths
        print("📁 Enter image paths (press Enter with empty line to finish):")
        image_paths = []
        
        while True:
            path = input("🖼️ Image path: ").strip()
            if not path:
                break
            if os.path.exists(path):
                image_paths.append(path)
                print(f"✅ Added: {path}")
            else:
                print(f"❌ File not found: {path}")
        
        if not image_paths:
            print("❌ No valid images provided")
            return
        
        print(f"\n📊 Processing {len(image_paths)} images...")
        
        # Crop all images
        result = cropper.crop_multiple_images(image_paths)
        
        print(f"\n📈 Results Summary:")
        print(f"   Total images: {result['total_images']}")
        print(f"   Successful crops: {result['successful_crops']}")
        print(f"   Failed crops: {result['failed_crops']}")
        print(f"   Output directory: {result['output_directory']}")
        
        # Show individual results
        print(f"\n📋 Individual Results:")
        for i, item in enumerate(result['results'], 1):
            print(f"\n   {i}. {os.path.basename(item['image_path'])}")
            if item['result']['success']:
                print(f"      ✅ Success: {item['result']['cropped_dimensions']}")
                print(f"      💾 Saved to: {item['result']['output_path']}")
            else:
                print(f"      ❌ Failed: {item['result']['error']}")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Main test function"""
    print("🎯 Intelligent Image Cropper Agent Test")
    print("="*60)
    print("🧠 Advanced cropping for product images with white backgrounds")
    print("✨ Features: Auto-centering, smart sizing, product detection")
    print("="*60)
    
    while True:
        print("\n🔧 Choose test type:")
        print("   [1] Test single image")
        print("   [2] Test multiple images")
        print("   [3] Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            test_single_image()
        elif choice == "2":
            test_multiple_images()
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
