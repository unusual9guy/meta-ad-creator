"""
Agent 2: Simple Creative Generator
Takes prompt from Agent 1 and feeds it directly to Nano Banana
"""

import json
import re
from typing import Dict, Any, Optional, List
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()

# Common font names to strip from prompts
COMMON_FONT_NAMES = [
    # Classic luxury fonts
    "Calgary", "Tan Pearl", "RoxboroughCF", "Roxborough CF", "Roxborough",
    # Popular serif fonts
    "Playfair Display", "Playfair", "Bodoni", "Bodoni Moda", "Trajan", "Didot",
    "Georgia", "Times New Roman", "Times", "Garamond", "Baskerville",
    # Popular sans-serif fonts
    "Montserrat", "Lato", "Roboto", "Open Sans", "Helvetica", "Arial",
    "Futura", "Gotham", "Proxima Nova", "Avenir", "Century Gothic",
    # Script and display fonts
    "Mafins", "Monalisa", "Script MT", "Brush Script", "Pacifico",
    # Other common fonts
    "Inter", "Poppins", "Source Sans", "Nunito", "Raleway", "Oswald",
    "Merriweather", "Libre Baskerville", "Crimson Text", "Cormorant",
]

class CreativeGeneratorAgent:
    """
    Agent 2: Simple creative generator that takes prompt and image
    Feeds prompt directly to Nano Banana
    """
    
    def __init__(self, api_key: Optional[str] = None, custom_font_names: Optional[List[str]] = None):
        """Initialize the creative generator agent"""
        # Use specific key for creative generation, fall back to general key
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY_CREATIVE") or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY_CREATIVE or GOOGLE_API_KEY environment variable.")
        
        self.client = genai.Client(api_key=self.api_key)
        
        # Combine common font names with any custom ones provided
        self.font_names_to_strip = COMMON_FONT_NAMES.copy()
        if custom_font_names:
            self.font_names_to_strip.extend(custom_font_names)
    
    def _strip_font_names_from_prompt(self, prompt: str, additional_fonts: Optional[List[str]] = None) -> str:
        """
        Remove all font name references from the prompt before sending to Nano Banana.
        The image generation model interprets font names as text to display,
        so we need to remove them completely.
        """
        cleaned_prompt = prompt
        
        # Add any additional fonts to strip
        fonts_to_remove = self.font_names_to_strip.copy()
        if additional_fonts:
            fonts_to_remove.extend(additional_fonts)
        
        # Remove duplicates and sort by length (longest first to avoid partial matches)
        fonts_to_remove = list(set(fonts_to_remove))
        fonts_to_remove.sort(key=len, reverse=True)
        
        # Try to parse as JSON and clean it
        try:
            # Clean markdown code blocks
            json_prompt = cleaned_prompt
            if json_prompt.startswith('```json'):
                json_prompt = json_prompt[7:]
            elif json_prompt.startswith('```'):
                json_prompt = json_prompt[3:]
            if json_prompt.endswith('```'):
                json_prompt = json_prompt[:-3]
            json_prompt = json_prompt.strip()
            
            # Find JSON object
            json_start = json_prompt.find('{')
            json_end = json_prompt.rfind('}')
            
            if json_start != -1 and json_end != -1:
                json_str = json_prompt[json_start:json_end+1]
                
                # Parse JSON
                prompt_json = json.loads(json_str)
                
                # Remove font-related fields and clean text fields
                def clean_json_object(obj):
                    if isinstance(obj, dict):
                        # Remove font-related keys entirely
                        keys_to_remove = []
                        for key in obj:
                            if key in ['font', 'font_instruction', 'warning']:
                                keys_to_remove.append(key)
                        for key in keys_to_remove:
                            del obj[key]
                        
                        # Clean text fields
                        for key, value in obj.items():
                            if key == "text" and isinstance(value, str):
                                # Remove font names from text content
                                for font_name in fonts_to_remove:
                                    # Case-insensitive replacement
                                    pattern = re.compile(re.escape(font_name), re.IGNORECASE)
                                    value = pattern.sub("", value)
                                # Clean up extra spaces
                                value = re.sub(r'\s+', ' ', value).strip()
                                obj[key] = value
                            elif isinstance(value, (dict, list)):
                                clean_json_object(value)
                    elif isinstance(obj, list):
                        for item in obj:
                            clean_json_object(item)
                
                clean_json_object(prompt_json)
                
                # Convert back to string
                cleaned_prompt = json.dumps(prompt_json, indent=2)
        except (json.JSONDecodeError, Exception):
            # If JSON parsing fails, do string-based cleaning
            pass
        
        # Also do string-based cleaning as a safety net
        for font_name in fonts_to_remove:
            # Remove font name references in various formats
            patterns = [
                # "font": "FontName"
                rf'"font"\s*:\s*["\']?{re.escape(font_name)}["\']?\s*,?',
                # "font_instruction": "..."
                rf'"font_instruction"\s*:\s*"[^"]*"\s*,?',
                # "warning": "..."
                rf'"warning"\s*:\s*"[^"]*"\s*,?',
                # Standalone font name (case insensitive)
                rf'\b{re.escape(font_name)}\b',
            ]
            for pattern in patterns:
                cleaned_prompt = re.sub(pattern, '', cleaned_prompt, flags=re.IGNORECASE)
        
        # Clean up any double commas, trailing commas before brackets
        cleaned_prompt = re.sub(r',\s*,', ',', cleaned_prompt)
        cleaned_prompt = re.sub(r',\s*([}\]])', r'\1', cleaned_prompt)
        cleaned_prompt = re.sub(r'([{[,])\s*,', r'\1', cleaned_prompt)
        
        # Add explicit instructions for image generation
        critical_instructions = """

CRITICAL INSTRUCTIONS FOR IMAGE GENERATION:

1. ASPECT RATIO: Generate the image in EXACTLY 1:1 aspect ratio (square format, 1080x1080 pixels).
   - The output MUST be a perfect square
   - Do NOT generate landscape or portrait images
   - Width and height MUST be equal

2. FONT NAMES: DO NOT display any font names as text in the generated image.
   - All text should be actual product copy (headlines, taglines, prices, features)
   - Never render font names like "Calgary", "Tan Pearl", "Playfair", etc. as visible text

3. PRODUCT: Keep the product as the central hero element, perfectly composed within the square frame.

"""
        cleaned_prompt = critical_instructions + cleaned_prompt
        
        return cleaned_prompt
    
    def generate_creative(self, image_path: str, prompt: str, product_description: str = "", 
                         logo_path: Optional[str] = None,
                         font_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate Meta ad creative by feeding prompt directly to Nano Banana
        
        Args:
            image_path: Path to the product image
            prompt: Structured prompt from Agent 1
            product_description: Product description for naming
            logo_path: Optional path to company logo image
            font_names: Optional list of font names used (to strip from prompt)
        
        Returns:
            Dictionary containing the result
        """
        try:
            # Create output directory if it doesn't exist
            output_dir = "data/output/creatives"
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
            
            # CRITICAL: Strip all font names from the prompt before sending to Nano Banana
            cleaned_prompt = self._strip_font_names_from_prompt(prompt, font_names)
            
            # Load the images
            image = Image.open(image_path)
            contents = [cleaned_prompt, image]
            
            # Add logo if provided
            if logo_path and os.path.exists(logo_path):
                logo_image = Image.open(logo_path)
                contents.append(logo_image)
            
            # Feed prompt and images directly to Nano Banana
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-image-preview",
                contents=contents,
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
                    "prompt_used": cleaned_prompt,
                    "original_prompt": prompt
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
