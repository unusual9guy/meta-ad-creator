"""
Test script for Background Remover Agent
Tests background removal using Nano Banana model
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from background_remover_agent import BackgroundRemoverAgent

load_dotenv()

def test_single_image():
    """Test removing background from a single image"""
    print("🧪 Testing Single Image Background Removal")
    print("="*60)
    
    try:
        # Initialize agent
        remover = BackgroundRemoverAgent()
        print("✅ Background Remover Agent initialized!")
        
        # Get image path
        image_path = input("🖼️ Enter image path: ").strip()
        
        if not os.path.exists(image_path):
            print(f"❌ Image not found: {image_path}")
            return
        
        print(f"📁 Processing: {image_path}")
        print("🎯 Removing background and replacing with white...")
        
        # Remove background
        result = remover.remove_background(image_path)
        
        if result["success"]:
            print("✅ Background removed successfully!")
            print(f"💾 Output saved to: {result['output_path']}")
            print(f"🖼️ Image generated: {result['image_generated']}")
            
            if result.get("result_text"):
                print(f"📝 Model response: {result['result_text'][:100]}...")
        else:
            print(f"❌ Background removal failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_multiple_images():
    """Test removing backgrounds from multiple images"""
    print("\n🧪 Testing Multiple Image Background Removal")
    print("="*60)
    
    try:
        # Initialize agent
        remover = BackgroundRemoverAgent()
        print("✅ Background Remover Agent initialized!")
        
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
        
        # Remove backgrounds from all images
        result = remover.remove_background_batch(image_paths)
        
        print(f"\n📈 Results Summary:")
        print(f"   Total images: {result['total_images']}")
        print(f"   Successful removals: {result['successful_removals']}")
        print(f"   Failed removals: {result['failed_removals']}")
        print(f"   Output directory: {result['output_directory']}")
        
        # Show individual results
        print(f"\n📋 Individual Results:")
        for i, item in enumerate(result['results'], 1):
            print(f"\n   {i}. {os.path.basename(item['image_path'])}")
            if item['result']['success'] and item['result'].get('image_generated'):
                print(f"      ✅ Success: {item['result']['output_path']}")
            else:
                print(f"      ❌ Failed: {item['result'].get('error', 'Unknown error')}")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Main test function"""
    print("🎯 Background Remover Agent Test")
    print("="*60)
    print("🧠 Uses Nano Banana to remove backgrounds and replace with white")
    print("✨ Perfect for preparing product images for Meta ad creatives")
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
