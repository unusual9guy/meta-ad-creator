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
    
    def _strip_font_names_from_prompt(self, prompt: str, additional_fonts: Optional[List[str]] = None, include_price: bool = True) -> str:
        """
        Clean the prompt while preserving font specifications.
        Only removes font names from text content fields, NOT from font specification fields.
        This allows the model to use the specified fonts while preventing font names from appearing as text.
        """
        cleaned_prompt = prompt
        
        # Add any additional fonts to check for in text content
        fonts_to_check = self.font_names_to_strip.copy()
        if additional_fonts:
            fonts_to_check.extend(additional_fonts)
        
        # Remove duplicates and sort by length (longest first to avoid partial matches)
        fonts_to_check = list(set(fonts_to_check))
        fonts_to_check.sort(key=len, reverse=True)
        
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
                prefix = json_prompt[:json_start]
                suffix = json_prompt[json_end+1:]
                
                # Parse JSON
                prompt_json = json.loads(json_str)
                
                # Clean text fields ONLY - preserve font specification fields
                def clean_text_fields_only(obj):
                    if isinstance(obj, dict):
                        # DO NOT remove font, font_instruction, or warning fields - these are specifications
                        # Only clean text content fields
                        for key, value in obj.items():
                            if key == "text" and isinstance(value, str):
                                # Remove font names from text content only
                                for font_name in fonts_to_check:
                                    # Case-insensitive replacement in text content
                                    pattern = re.compile(re.escape(font_name), re.IGNORECASE)
                                    value = pattern.sub("", value)
                                # Clean up extra spaces
                                value = re.sub(r'\s+', ' ', value).strip()
                                obj[key] = value
                            elif isinstance(value, (dict, list)):
                                clean_text_fields_only(value)
                    elif isinstance(obj, list):
                        for item in obj:
                            clean_text_fields_only(item)
                
                # Remove pricing elements if include_price is False
                def remove_pricing_elements(obj):
                    if isinstance(obj, dict):
                        if not include_price:
                            if 'pricing_display' in obj:
                                del obj['pricing_display']
                            if 'limited_time_offer' in obj:
                                del obj['limited_time_offer']
                        for key, value in obj.items():
                            if isinstance(value, (dict, list)):
                                remove_pricing_elements(value)
                    elif isinstance(obj, list):
                        for item in obj:
                            remove_pricing_elements(item)
                
                # Clean text fields (remove font names from text content)
                clean_text_fields_only(prompt_json)
                
                # Remove pricing if needed
                remove_pricing_elements(prompt_json)
                
                # Convert back to string
                cleaned_prompt = prefix + json.dumps(prompt_json, indent=2) + suffix
        except (json.JSONDecodeError, Exception):
            # If JSON parsing fails, do minimal string-based cleaning of text content only
            # Don't remove font specifications
            pass
        
        # Add explicit instructions for image generation with variety
        import random
        
        # Randomize design elements for variety
        background_styles = [
            "warm beige gradient with soft shadows",
            "cool gray minimalist with subtle texture",
            "natural wooden surface with soft lighting",
            "marble texture with elegant shadows",
            "soft fabric texture with depth",
            "muted earth tones with natural feel",
            "clean white with dramatic product shadows",
            "soft pastel gradient (peach to cream)",
            "dark moody background with spotlight on product",
            "rustic textured background with warm lighting"
        ]
        
        layout_styles = [
            "product on left, text on right",
            "product centered, text above and below",
            "product on right, text on left", 
            "product bottom-center, text at top",
            "product slightly off-center with asymmetric text layout",
            "diagonal composition with dynamic text placement"
        ]
        
        typography_styles = [
            "bold modern sans-serif headlines with thin body text",
            "elegant serif headlines with clean sans-serif details",
            "minimalist typography with lots of white space",
            "bold statement typography with high contrast",
            "refined luxury typography with subtle letter-spacing"
        ]
        
        color_schemes = [
            "warm neutrals (beige, cream, tan, brown)",
            "cool elegance (gray, silver, white, charcoal)",
            "earthy luxe (olive, terracotta, gold, cream)",
            "modern minimal (black, white, single accent color)",
            "soft pastels (blush, sage, lavender, cream)"
        ]
        
        selected_bg = random.choice(background_styles)
        selected_layout = random.choice(layout_styles)
        selected_typo = random.choice(typography_styles)
        selected_colors = random.choice(color_schemes)
        
        critical_instructions = f"""

CRITICAL INSTRUCTIONS FOR IMAGE GENERATION:

1. ASPECT RATIO: Generate the image in EXACTLY 1:1 aspect ratio (square format, 1080x1080 pixels).
   - The output MUST be a perfect square
   - Width and height MUST be equal

2. UNIQUE CREATIVE DIRECTION FOR THIS AD:
   - BACKGROUND STYLE: {selected_bg}
   - LAYOUT: {selected_layout}
   - TYPOGRAPHY APPROACH: {selected_typo}
   - COLOR SCHEME: {selected_colors}
   
3. PROFESSIONAL QUALITY REQUIREMENTS:
   - This must look like it was created by a professional graphic designer at a top agency
   - Study high-end brand ads from Apple, Nike, Dyson, Bang & Olufsen for inspiration
   - Use sophisticated color grading and subtle shadows
   - Typography should be perfectly kerned and balanced
   - Negative space is your friend - don't overcrowd
   - The overall feel should be premium, polished, and aspirational
   - Avoid generic "template" looks - make it feel custom and crafted
   - Lighting should be soft, directional, and create depth
   - Shadows should be realistic and grounded

4. FONT USAGE - CRITICAL:
   - The "font" field in the JSON is a TECHNICAL SPECIFICATION telling you which font to USE for rendering
   - You MUST use the exact font specified in each "font" field to render the corresponding text
   - The font name in the "font" field is NOT text to display - it's a specification of which font to use
   - NEVER display font names (like "Playfair Display", "Calgary", "Montserrat", etc.) as visible text in the image
   - Use the specified fonts to render the actual product text (headlines, taglines, etc.)
   - Example: If font is "Playfair Display" and text is "ELEGANT DINING", use Playfair Display font to render "ELEGANT DINING" - do NOT display "Playfair Display" as text
   - All displayed text should be actual product copy, NOT font names

5. PROMOTION TEXT - CRITICAL - NEVER ABBREVIATE:
   - **THIS IS THE MOST IMPORTANT RULE: EVERY WORD IN THE PROMOTION MUST BE FULLY SPELLED OUT**
   - If the promotion is "30% OFF WINTER SALE", you MUST render ALL FOUR WORDS: "30%" + "OFF" + "WINTER" + "SALE"
   - **ABSOLUTELY FORBIDDEN - NEVER DO THESE:**
     * "W" instead of "WINTER" - THIS IS WRONG
     * "S" instead of "SALE" - THIS IS WRONG  
     * "O" instead of "OFF" - THIS IS WRONG
     * ANY single letter replacing ANY word - THIS IS WRONG
   - **WRONG EXAMPLES (NEVER RENDER THESE):**
     * "30% W SALE" - WRONG (Winter is abbreviated)
     * "30% OFF W SALE" - WRONG (Winter is abbreviated)
     * "30% O W S" - WRONG (all words abbreviated)
     * "NATURAL ELEGANCE, 30% W SALE" - WRONG (Winter abbreviated)
   - **CORRECT EXAMPLES (DO THESE):**
     * "30% OFF WINTER SALE" - CORRECT (all words spelled out)
     * "NATURAL ELEGANCE, 30% OFF WINTER SALE" - CORRECT
     * "CRAFTED BEAUTY - 30% OFF WINTER SALE" - CORRECT
   - Copy the promotion text CHARACTER BY CHARACTER - do not summarize or shorten
   - **DO NOT use pipe symbol "|" as a separator** - use dashes or commas
   - Check every letter before rendering - if any word is a single letter, you made a mistake

6. PRICING: {"DO NOT include any pricing information, price tags, discount badges, or pricing elements anywhere in the image. Completely exclude all pricing-related visual elements." if not include_price else "Include pricing information as specified in the prompt."}

7. PRODUCT INTEGRATION - CRITICAL FOR REALISM:
   - The product MUST look like it BELONGS in the scene, not pasted on top
   - **LIGHTING MATCH**: The product's lighting direction, intensity, and color temperature MUST match the background
     * If background has dramatic side lighting → product should have matching side highlights/shadows
     * If background is warm-toned → product should have warm color cast
     * If background is cool/dark → product should reflect that ambient tone
   - **SHADOWS**: Add realistic ground shadows and contact shadows that anchor the product to the surface
   - **REFLECTIONS**: If on reflective surface (marble, glass), add subtle product reflections
   - **COLOR HARMONY**: The product should share color tones with the background environment
   - **EDGE BLENDING**: No harsh cutout edges - product should blend naturally into the scene
   - The goal is photorealistic compositing, as if the product was actually photographed in that setting
   - Study professional product photography - the lighting ALWAYS matches between product and environment

8. CTA BUTTON - MUST BLEND WITH BACKGROUND (NOT POP OUT):
   - The CTA must feel INTEGRATED into the design, like it belongs there naturally
   - CRITICAL: Match the background tone! For DARK/SMOKY backgrounds, use dark CTA styling
   - NEVER use gold/yellow rectangles on dark backgrounds - they look cheap and out of place
   - CREATIVE OPTIONS (choose based on background):
     * **DARK BACKGROUNDS**: Floating text only (white/cream), frosted glass effect, subtle glow behind text, or translucent dark button
     * **LIGHT BACKGROUNDS**: Text with underline accent, soft filled pill in muted tone, or subtle colored fill
     * **WARM BACKGROUNDS**: Warm-toned text or very soft earth-tone fill
   - AVOID: Bordered rectangles, contrasting colors that pop out, web-button aesthetics
   - The CTA should look like premium brand advertising, NOT a website button pasted on

9. TYPOGRAPHY - MUST BE BOLD, DISTINCTIVE, AND HIGH-IMPACT:
   - **ABSOLUTELY FORBIDDEN**: Default system fonts, thin/light weights, basic Microsoft Word fonts, Arial, Calibri, Times New Roman vibes
   - **HEADLINES MUST HAVE WEIGHT**: Use BOLD, BLACK, or EXTRA-BOLD weights - thin fonts look weak and forgettable
   - **CHARACTER IS MANDATORY**: 
     * High-contrast serifs with dramatic thick-thin stroke variation
     * Ultra-condensed or ultra-extended proportions that command attention
     * Distinctive display typefaces with artistic personality
     * Strong geometric sans-serifs with confident weight
   - **NEVER USE**: Light, thin, or regular weights for headlines - they look like placeholder text
   - **VISUAL HIERARCHY THROUGH WEIGHT**: Headline = heaviest weight, Tagline = medium weight, CTA = confident medium-bold
   - **LETTER-SPACING**: Headlines can use tight tracking for impact or wide tracking for elegance - NEVER default spacing
   - The typography should be the FIRST thing that catches the eye after the product
   - Study typography from Nike, Apple, luxury fashion brands - NEVER timid, always confident

9. LAYOUT VARIETY - CRITICAL:
   - DO NOT always use the same layout with 4 feature icons below the headline
   - Choose DIFFERENT layouts for different ads:
     * Minimal: Just headline + tagline + CTA (no feature icons)
     * Editorial: Product hero with elegant text overlay
     * Sidebar benefits: Text benefits on one side, product on other
     * Bold statement: Large headline dominates the design
   - For LUXURY products: NEVER use feature icons - keep it minimal and elegant
   - Feature icons are optional and should only be used when appropriate for the brand

"""
        cleaned_prompt = critical_instructions + cleaned_prompt
        
        return cleaned_prompt
    
    def generate_creative(self, image_path: str, prompt: str, product_description: str = "", 
                         logo_path: Optional[str] = None,
                         font_names: Optional[List[str]] = None,
                         include_price: bool = True) -> Dict[str, Any]:
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
            # Also remove pricing elements if include_price is False
            cleaned_prompt = self._strip_font_names_from_prompt(prompt, font_names, include_price=include_price)
            
            # Load the images
            image = Image.open(image_path)
            contents = [cleaned_prompt, image]
            
            # Add logo if provided
            if logo_path and os.path.exists(logo_path):
                logo_image = Image.open(logo_path)
                contents.append(logo_image)
            
            # Try Gemini 3 Pro first, fallback to Gemini 2.5 Flash
            model_name = "models/gemini-3-pro-image-preview"
            try:
                # Try Gemini 3 Pro first
                response = self.client.models.generate_content(
                    model="models/gemini-3-pro-image-preview",
                    contents=contents,
                )
            except Exception as pro_error:
                # Fallback to Gemini 2.5 Flash
                try:
                    response = self.client.models.generate_content(
                        model="gemini-2.5-flash-image",
                        contents=contents,
                    )
                    model_name = "gemini-2.5-flash-image"
                except Exception as fallback_error:
                    # If both fail, raise the original error
                    raise pro_error
            
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
                    "original_prompt": prompt,
                    "model_used": model_name
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
