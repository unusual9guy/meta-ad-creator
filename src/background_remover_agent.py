"""
Background Remover Agent
Uses Google's Nano Banana model to remove backgrounds and replace with white
"""

from typing import Dict, Any, Optional
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()

class BackgroundRemoverAgent:
    """
    Agent for removing backgrounds from product images using Nano Banana
    Replaces backgrounds with white for clean product images
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the background remover agent"""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
        
        self.client = genai.Client(api_key=self.api_key)
    
    def remove_background(self, image_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Remove background from product image and replace with white
        
        Args:
            image_path: Path to the input image
            output_path: Optional output path (if None, saves to white_bg_images/)
        
        Returns:
            Dictionary containing the result
        """
        try:
            # Create output directory
            if output_path is None:
                white_bg_dir = "white_bg_images"
                os.makedirs(white_bg_dir, exist_ok=True)
                
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                extension = os.path.splitext(image_path)[1]
                output_path = os.path.join(white_bg_dir, f"{base_name}_white_bg{extension}")
            
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            # Load the image
            image = Image.open(image_path)
            
            # Create the prompt for background removal
            prompt = """
            Remove the background from this product image and replace it with a clean white background. 
            
            Requirements:
            - Keep the product exactly as it is - do not modify, resize, or change the product
            - Remove all background elements completely
            - Replace with pure white background (#FFFFFF)
            - Maintain the product's original colors, shadows, and details
            - Ensure the product is clearly visible against the white background
            - The final image should look like a professional product photo with white background
            - Do not add any text, logos, or additional elements
            - Focus only on the product with clean white background
            """
            
            print("🔄 Processing image with Nano Banana...")
            print("🎯 Removing background and replacing with white...")
            
            # Call Nano Banana model
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-image-preview",
                contents=[prompt, image],
            )
            
            result_text = ""
            processed_image = None
            
            # Process the response
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    result_text += part.text
                elif part.inline_data is not None:
                    # Save the generated image
                    processed_image = Image.open(BytesIO(part.inline_data.data))
                    processed_image.save(output_path, quality=95)
                    print(f"✅ Background removed successfully!")
                    print(f"💾 Saved to: {output_path}")
            
            if processed_image is None:
                # If no image was generated, save the text response
                with open(output_path.replace('.jpg', '_result.txt'), 'w', encoding='utf-8') as f:
                    f.write(result_text)
                print("⚠️ No image generated, saved text response instead")
            
            return {
                "success": True,
                "message": "Background removed and replaced with white",
                "output_path": output_path,
                "original_path": image_path,
                "result_text": result_text,
                "image_generated": processed_image is not None,
                "metadata": {
                    "model_used": "gemini-2.5-flash-image-preview",
                    "operation": "background_removal"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output_path": None,
                "image_generated": False,
                "metadata": {
                    "model_used": "gemini-2.5-flash-image-preview",
                    "operation": "background_removal"
                }
            }
    
    def remove_background_batch(self, image_paths: list, output_dir: str = "white_bg_images") -> Dict[str, Any]:
        """
        Remove backgrounds from multiple images
        
        Args:
            image_paths: List of image paths
            output_dir: Directory to save processed images
        
        Returns:
            Dictionary containing results for all images
        """
        results = []
        successful_removals = 0
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"🔄 Processing {len(image_paths)} images...")
        
        for i, image_path in enumerate(image_paths, 1):
            try:
                print(f"\n📸 Processing {i}/{len(image_paths)}: {os.path.basename(image_path)}")
                
                # Generate output path
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                extension = os.path.splitext(image_path)[1]
                output_path = os.path.join(output_dir, f"{base_name}_white_bg{extension}")
                
                # Remove background
                result = self.remove_background(image_path, output_path)
                results.append({
                    "image_path": image_path,
                    "result": result
                })
                
                if result["success"] and result.get("image_generated"):
                    successful_removals += 1
                    print(f"✅ Success: {os.path.basename(output_path)}")
                else:
                    print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                results.append({
                    "image_path": image_path,
                    "result": {
                        "success": False,
                        "error": str(e),
                        "image_generated": False
                    }
                })
                print(f"❌ Error processing {os.path.basename(image_path)}: {str(e)}")
        
        return {
            "success": successful_removals > 0,
            "total_images": len(image_paths),
            "successful_removals": successful_removals,
            "failed_removals": len(image_paths) - successful_removals,
            "results": results,
            "output_directory": output_dir
        }
