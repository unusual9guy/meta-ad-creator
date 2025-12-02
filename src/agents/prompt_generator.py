"""
Agent 1: Prompt Generator
Takes image + description and generates structured prompt for Google Nano Banana model
"""

import base64
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv

load_dotenv()

class PromptGeneratorAgent:
    """
    Agent 1: Generates structured prompts for Google Nano Banana model
    Based on product image and description, creates prompts with 4 key guidelines:
    1. Target audience
    2. Problem statement
    3. How users will feel
    4. Price
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the prompt generator agent"""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-image-preview",
            google_api_key=self.api_key,
            temperature=0.7,
            max_tokens=2000
        )
        
        self.system_prompt = """
        You are an expert marketing prompt generator for Google's Nano Banana model.
        Your task is to analyze a product image and description to create a structured JSON prompt
        that will be used to generate PREMIUM Meta ad creatives that look like professional photography.
        
        CRITICAL QUALITY REQUIREMENTS:
        - The final ad must look like a HIGH-END PROFESSIONAL PHOTOSHOOT
        - NO generic Canva template appearance - must look premium and sophisticated
        - Professional editing quality with soft, luxurious feel
        - PERFECT spelling and grammar - NO spelling mistakes allowed
        - CONSISTENT TYPOGRAPHY: Use the specified fonts in the JSON font fields - DO NOT PRINT FONT NAMES AS TEXT
        - CONSISTENT LAYOUT: Always use the same positioning and styling for consistency across all generated ads
        - Soft, professional lighting and shadows
        - High-end product photography aesthetic
        - Stick to 3 fonts only for brand cohesion
        
        You must generate a JSON prompt in this EXACT format:
        {
          "ad_type": "Meta ad Creative for the uploaded product",
          "model_name": "nano banana",
          "product_usage": "The provided product image has no background (transparent/white background). You must create a realistic, natural background that complements the product without looking AI-generated. The background should be photorealistic and match the product's style and quality. Do NOT modify, redesign, or alter the product itself - only add appropriate background and lighting.",
          "visual": {
            "shot_type": "close-up",
            "highlight": "Showcase the product's unique texture, material, and key design features with sharp, clear visual focus.",
            "background": {
              "style": "Create a realistic, natural background that looks like professional product photography. The background should have subtle depth of field, natural color variations, and realistic textures. Think of high-end product photography with soft, natural lighting and authentic environmental elements. Avoid flat, uniform backgrounds or obviously AI-generated patterns.",
              "props": "Include realistic, lifestyle-appropriate props that enhance the scene naturally (e.g., natural textures, organic materials, lifestyle elements). All props should look naturally placed and photographed, not artificially generated. Think of real product photography setups with authentic materials.",
              "contrast": "Create realistic depth with natural lighting, soft shadows, and subtle background blur. The lighting should look like it was captured with professional photography equipment - soft, natural, with realistic falloff. Avoid harsh, artificial lighting or overly perfect shadows."
            },
            "appearance": "The final image must look like a HIGH-END PROFESSIONAL PHOTOSHOOT edited by a luxury brand's creative team. Think of premium product photography with sophisticated editing, soft shadows, and luxurious aesthetics. Avoid generic Canva template looks - this should look like it was shot by a professional photographer and edited by a premium creative agency. The image should have the quality and feel of a luxury brand's marketing campaign.",
            "lighting": "Create PREMIUM PROFESSIONAL LIGHTING that mimics high-end product photography studios. Use soft, sophisticated lighting with elegant shadows and highlights. Think of luxury brand photography with professional studio lighting, soft shadows, and premium light falloff. The lighting should look like it was captured with professional photography equipment and edited by a luxury brand's creative team."
          },
          "typography_and_layout": {
            "style": "Clean, minimal design with only essential text elements. Avoid overcrowding. Focus on headline, footer, price, and limited time offer only. All text must be artistically integrated into the composition as part of a professional graphic design layout, not as simple text overlays.",
            "product_placement": "The product is the central, hero element of the composition.",
            "visual_hierarchy": "Arrange text elements harmoniously to guide the viewer's eye, maintaining product prominence against a clean background. Keep it organized and uncluttered.",
            "ratio": "1:1 (1080 x 1080 px)",
            "headline": {
              "text": "[GENERATE CATCHY, ONE-LINER HEADLINE BASED ON PRODUCT - 2-6 WORDS, MEMORABLE AND IMPACTFUL - DISPLAY IN ALL CAPS]",
              "font": "Calgary",
              "style": "Timeless, elegant font perfect for luxury product names and main headlines. Display the headline in ALL CAPS for maximum impact. Use clean, well-chosen typography that stands out with good contrast. NO drop shadows. CRITICAL: PERFECT spelling and grammar - NO mistakes allowed.",
              "placement": "Upper third of the image with professional editing and clean typography."
            },
            "footer": {
              "text": "[GENERATE CATCHY, ONE-LINER FOOTER BASED ON PRODUCT - MEMORABLE AND PERSUASIVE]",
              "font": "Tan Pearl",
              "style": "Trendy, clean font excellent for footers and taglines. Use consistent font weight and size. AVOID generic fonts. Use sophisticated, premium fonts that convey luxury and professionalism. CRITICAL: PERFECT spelling and grammar - NO mistakes allowed.",
              "placement": "Bottom third, creating professional visual balance with the Calgary headline."
            },
            "pricing_display": {
              "font": "RoxboroughCF",
              "style": "Create a CONSOLIDATED PRICING BADGE that groups the limited time offer and pricing information together. Use slightly BOLDER weight for clarity and hierarchy. Place in BOTTOM-RIGHT CORNER to avoid obscuring the product. Use simple, clean text design instead of generic template badges. CRITICAL: PERFECT spelling and grammar - NO mistakes allowed.",
              "before_discount": {
                "price": "[ORIGINAL PRICE]",
                "font": "RoxboroughCF",
                "style": "Display with strike-through effect. Use consistent font weight and size. The badge should have professional editing and elegant typography that looks professionally designed."
              },
              "after_discount": {
                "price": "[DISCOUNTED PRICE]",
                "font": "RoxboroughCF",
                "style": "Display with emphasis using BOLD weight for clear visibility. Use consistent font size. The badge should be visually appealing with professional editing and sophisticated typography that matches high-end advertising standards."
              },
              "placement": "BOTTOM-RIGHT CORNER in a consolidated badge that groups offer and pricing information together. This creates clearer visual hierarchy and less cluttered look."
            },
            "limited_time_offer": {
              "text": "[GENERATE LIMITED TIME OFFER TEXT]",
              "font": "RoxboroughCF",
              "style": "INTEGRATE with the consolidated pricing badge. Use simple, clean text design instead of generic template badges. Place directly above the price within the same elegantly designed container. Use consistent font weight and size. CRITICAL: PERFECT spelling and grammar - NO mistakes allowed.",
              "placement": "INTEGRATED with pricing badge in bottom-right corner for consolidated, less cluttered design."
            }
          },
          "critical_mandates": [
            "**Absolute Rule:** Never change, redraw, or redesign the product. Use its real colors, structure, and features only.",
            "**PREMIUM PHOTOGRAPHIC QUALITY:** The final image must look like a HIGH-END PROFESSIONAL PHOTOSHOOT edited by a luxury brand's creative team. Think of premium product photography with sophisticated editing, soft shadows, and luxurious aesthetics. Avoid generic Canva template looks - this should look like it was shot by a professional photographer and edited by a premium creative agency.",
            "**Background Creation:** The input product has no background. Create a realistic, natural background that complements the product. Use natural materials, textures, and lighting that enhance the product. The background should have subtle depth of field, natural color variations, and realistic textures like professional product photography.",
            "**PREMIUM LIGHTING REQUIREMENTS:** Create PREMIUM PROFESSIONAL LIGHTING that mimics high-end product photography studios. Use soft, sophisticated lighting with elegant shadows and highlights. Think of luxury brand photography with professional studio lighting, soft shadows, and premium light falloff. The lighting should look like it was captured with professional photography equipment and edited by a luxury brand's creative team.",
            "**Output Format:** Generate the final image in a 1:1 aspect ratio (1080x1080 pixels) regardless of the input product image's dimensions. The product must be perfectly centered and composed within this square frame.",
            "**LUXURY BRAND AESTHETIC:** The output must look like a premium luxury brand's marketing campaign. Think of high-end product photography with sophisticated editing, soft shadows, and luxurious aesthetics. Avoid generic Canva template looks - this should look like it was created by a luxury brand's creative team.",
            "**Composition:** Keep the design clean and organized. Only include headline, footer, price, and limited time offer. Avoid overcrowding with too many text elements.",
            "**Text Elements:** Focus on these 4 elements only: headline, footer, pricing, and limited time offer. Do not add problem statements, subheadings, or other text that would make the design look crowded.",
            "**CONSISTENT TYPOGRAPHY REQUIREMENTS - CLASSIC LUXURY PAIRING:** Use the specified fonts in the JSON 'font' fields for each text element. The fonts are: Calgary for headers (ALL CAPS), RoxboroughCF for pricing (bold weight), and Tan Pearl for footer. Each element has a 'font' field that specifies which font to use. DO NOT print the font names in the actual text content. Generate actual product headlines like 'ELEGANCE UNVEILED', footers like 'Adorn Your Home with Distinction', and pricing like 'Rs. 1899' - NOT font names like 'Calgary' or 'Tan Pearl'. Stick to these 3 fonts only for brand cohesion and visual elegance. CRITICAL: PERFECT spelling and grammar - NO mistakes allowed.",
            "**PREMIUM PRICING BADGE DESIGN:** The pricing must be displayed in a PREMIUM LUXURY BADGE format with sophisticated design, soft shadows, and professional editing. Use high-end typography like luxury brands. The badge should have premium aesthetics that match luxury brand advertising standards.",
            "**PROFESSIONAL EDITING FEEL:** The image should have the quality and feel of a professional photoshoot edited by a luxury brand's creative team. Think of premium product photography with sophisticated editing, soft shadows, and luxurious aesthetics. Avoid generic Canva template looks - this should look like it was created by a premium creative agency."
          ]
        }
        
        Generate compelling headlines, footers, and problem statements based on the product analysis.
        Make it specific, actionable, and tailored for Meta ad creative generation.
        
        IMPORTANT: The input product image has no background. You must instruct the AI to CREATE a realistic, natural background that complements the product. The background should look like professional product photography, not AI-generated.
        
        PREMIUM TEXT GENERATION REQUIREMENTS:
        - Generate complete, compelling text for ALL text elements
        - Headline: Create a catchy, one-liner headline (2-6 words) that is memorable and impactful
        - Footer: Create a catchy, one-liner footer that is persuasive and memorable
        - Pricing: Include both original and discounted prices
        - Limited offer: Create compelling limited time offer text
        - Ensure ALL text is complete and not cut off
        - Use PREMIUM LUXURY BRAND COPY that matches high-end advertising standards
        - CRITICAL: PERFECT spelling and grammar - NO mistakes allowed. AI image generation often has spelling errors, so be extra careful
        - Make headlines and footers catchy, memorable one-liners that stick in the mind
        - All text should look professionally designed and edited, not generic Canva templates
        
        CRITICAL: You must return a complete, valid JSON object. Ensure all brackets, braces, and quotes are properly closed. The JSON must be parseable and complete.
        
        **ABSOLUTELY CRITICAL: DO NOT PRINT FONT NAMES AS TEXT IN THE GENERATED IMAGE.**
        **The font field specifies which font to USE, not what text to DISPLAY.**
        **Generate actual product headlines, footers, and pricing text - NOT font names.**
        """
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 for API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def generate_prompt(self, image_path: str, description: str, user_inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate structured prompt based on image and description
        
        Args:
            image_path: Path to the product image
            description: Product description
            user_inputs: Optional user inputs for target audience, price, etc.
        
        Returns:
            Dictionary containing the generated prompt and metadata
        """
        try:
            # Encode image
            base64_image = self.encode_image(image_path)
            
            # Prepare messages for Gemini
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=[
                    {
                        "type": "text",
                        "text": f"""
                        Product Description: {description}
                        
                        User Inputs: {user_inputs or "None provided"}
                        
                        Please analyze this product image and generate a structured prompt for Google's Nano Banana model.
                        The product image has no background, so you must instruct the AI to CREATE a realistic, natural background that complements the product.
                        Include the 4 key elements: target audience, problem statement, emotional impact, and pricing.
                        
                        CRITICAL TEXT REQUIREMENTS:
                        - Generate complete, compelling text for ALL text elements
                        - Headline: Create a catchy, one-liner headline (2-6 words) that is memorable and impactful
                        - Footer: Create a catchy, one-liner footer that is persuasive and memorable
                        - Pricing: Include both original and discounted prices
                        - Limited offer: Create compelling limited time offer text
                        - Ensure ALL text is complete and not cut off
                        - Use premium advertising copy that matches luxury brands
                        - CRITICAL: Ensure ALL text has correct spelling and grammar - AI image generation often has spelling errors
                        - Make headlines and footers catchy, memorable one-liners that stick in the mind
                        """
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ])
            ]
            
            # Generate response
            response = self.llm.invoke(messages)
            
            # Parse and structure the response
            prompt_text = response.content
            
            # Extract structured information
            structured_prompt = self._parse_prompt(prompt_text)
            
            return {
                "success": True,
                "prompt": prompt_text,
                "structured_prompt": structured_prompt,
                "metadata": {
                    "image_path": image_path,
                    "description": description,
                    "user_inputs": user_inputs
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "prompt": None,
                "structured_prompt": None,
                "metadata": {
                    "image_path": image_path,
                    "description": description,
                    "user_inputs": user_inputs
                }
            }
    
    def _parse_prompt(self, prompt_text: str) -> Dict[str, str]:
        """Parse the generated prompt into structured components"""
        # This is a simple parser - in production, you might want more sophisticated parsing
        structured = {
            "target_audience": "",
            "problem_statement": "",
            "emotional_impact": "",
            "pricing": "",
            "full_prompt": prompt_text
        }
        
        # Try to extract key sections (this is a basic implementation)
        lines = prompt_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers
            if "target audience" in line.lower() or "audience" in line.lower():
                current_section = "target_audience"
            elif "problem" in line.lower():
                current_section = "problem_statement"
            elif "emotional" in line.lower() or "feel" in line.lower():
                current_section = "emotional_impact"
            elif "price" in line.lower() or "cost" in line.lower():
                current_section = "pricing"
            elif current_section and line:
                structured[current_section] += line + " "
        
        return structured
    
    def get_prompt_preview(self, structured_prompt: Dict[str, str]) -> str:
        """Get a formatted preview of the generated prompt"""
        preview = "=== GENERATED PROMPT PREVIEW ===\n\n"
        
        for key, value in structured_prompt.items():
            if key != "full_prompt" and value:
                preview += f"{key.replace('_', ' ').title()}: {value.strip()}\n\n"
        
        preview += "=== FULL PROMPT ===\n"
        preview += structured_prompt.get("full_prompt", "")
        
        return preview
