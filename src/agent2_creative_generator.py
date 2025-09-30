"""
Agent 2: Simple Creative Generator
Takes prompt from Agent 1 and feeds it directly to Nano Banana
"""

from typing import Dict, Any, Optional
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()

class CreativeGeneratorAgent:
    """
    Agent 2: Simple creative generator that takes prompt and image
    Feeds prompt directly to Nano Banana
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the creative generator agent"""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
        
        self.client = genai.Client(api_key=self.api_key)
    
    def generate_creative(self, image_path: str, prompt: str, product_description: str = "") -> Dict[str, Any]:
        """
        Generate Meta ad creative by feeding prompt directly to Nano Banana
        
        Args:
            image_path: Path to the product image
            prompt: Structured prompt from Agent 1
            product_description: Product description for naming
        
        Returns:
            Dictionary containing the result
        """
        try:
            # Create output directory if it doesn't exist
            output_dir = "generated_images"
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate output filename based on product description
            if product_description:
                # Clean the description for filename
                clean_name = "".join(c for c in product_description if c.isalnum() or c in (' ', '-', '_')).rstrip()
                clean_name = clean_name.replace(' ', '_').lower()
                filename = f"{clean_name}_meta_ad_creative.jpg"
            else:
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                filename = f"{base_name}_meta_ad_creative.jpg"
            
            output_path = os.path.join(output_dir, filename)
            
            # Load the image
            image = Image.open(image_path)
            
            # Feed prompt directly to Nano Banana
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-image-preview",
                contents=[prompt, image],
            )
            
            # Process the response
            result_text = ""
            generated_image = None
            
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    result_text += part.text
                elif part.inline_data is not None:
                    generated_image = Image.open(BytesIO(part.inline_data.data))
                    generated_image.save(output_path)
            
            # Save text result if no image was generated
            if generated_image is None:
                with open(output_path.replace('.jpg', '_result.txt'), 'w', encoding='utf-8') as f:
                    f.write(result_text)
            
            return {
                "success": True,
                "creative_result": result_text,
                "output_path": output_path,
                "metadata": {
                    "image_path": image_path,
                    "prompt_used": prompt
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "creative_result": None,
                "output_path": None,
                "metadata": {
                    "image_path": image_path,
                    "prompt_used": prompt
                }
            }
