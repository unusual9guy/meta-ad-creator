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
        - Premium typography and layout that matches luxury brands
        - Soft, professional lighting and shadows
        - High-end product photography aesthetic
        
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
              "text": "[GENERATE CATCHY, ONE-LINER HEADLINE BASED ON PRODUCT - 2-6 WORDS, MEMORABLE AND IMPACTFUL]",
              "style": "Use MODERN ELEGANT SERIF FONTS like Playfair Display, Bodoni Moda, or Trajan for luxury and sophistication. These fonts have high contrast between thick and thin strokes, adding refinement. For modern feel, consider Mafins or Monalisa. AVOID generic fonts like Arial, Times New Roman, or basic system fonts. NO drop shadows - use clean, well-chosen fonts that stand out with good contrast. CRITICAL: PERFECT spelling and grammar - NO mistakes allowed.",
              "placement": "Upper third of the image, rendered in a modern elegant serif font that is part of the scene's design with professional editing and clean typography."
            },
            "footer": {
              "text": "[GENERATE CATCHY, ONE-LINER FOOTER BASED ON PRODUCT - MEMORABLE AND PERSUASIVE]",
              "style": "Use CLEAN SANS-SERIF FONTS like Montserrat, Lato, or Roboto for excellent readability and modern contrast with the serif headline. This creates visual balance and professional typography pairing. AVOID generic fonts like Arial, Times New Roman, or basic system fonts. Use sophisticated, premium fonts that convey luxury and professionalism. CRITICAL: PERFECT spelling and grammar - NO mistakes allowed.",
              "placement": "Bottom third, using a clean sans-serif font that complements the serif headline and creates professional visual balance."
            },
            "pricing_display": {
              "style": "Create a CONSOLIDATED PRICING BADGE that groups the limited time offer and pricing information together. Use CLEAN SANS-SERIF FONTS like Montserrat, Lato, or Roboto for excellent readability. Place in BOTTOM-RIGHT CORNER to avoid obscuring the product. Use simple, clean text design instead of generic template badges. AVOID generic fonts like Arial, Times New Roman. The badge should have professional editing and premium aesthetics. CRITICAL: PERFECT spelling and grammar - NO mistakes allowed.",
              "before_discount": {
                "price": "[ORIGINAL PRICE]",
                "style": "Display with strike-through effect using clean sans-serif typography. Use sophisticated, premium fonts that convey luxury and professionalism. The badge should have professional editing and elegant typography that looks professionally designed."
              },
              "after_discount": {
                "price": "[DISCOUNTED PRICE]",
                "style": "Display with emphasis using clean sans-serif typography. Use sophisticated, premium fonts that convey luxury and professionalism. The badge should be visually appealing with professional editing and sophisticated typography that matches high-end advertising standards."
              },
              "placement": "BOTTOM-RIGHT CORNER in a consolidated badge that groups offer and pricing information together. This creates clearer visual hierarchy and less cluttered look."
            },
            "limited_time_offer": {
              "text": "[GENERATE LIMITED TIME OFFER TEXT]",
              "style": "INTEGRATE with the consolidated pricing badge using CLEAN SANS-SERIF FONTS like Montserrat, Lato, or Roboto. Use simple, clean text design instead of generic template badges. Place directly above the price within the same elegantly designed container. AVOID generic fonts like Arial, Times New Roman. Use sophisticated, premium fonts that convey luxury and professionalism. CRITICAL: PERFECT spelling and grammar - NO mistakes allowed.",
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
            "**PREMIUM TYPOGRAPHY REQUIREMENTS:** Use PREMIUM LUXURY BRAND TYPOGRAPHY like Chanel, Louis Vuitton, or Apple - elegant serif fonts, sophisticated sans-serif, or refined script fonts. AVOID generic, unprofessional fonts like Arial, Times New Roman, or basic system fonts. Use sophisticated, premium fonts that convey luxury and professionalism. All text elements should use professional typography that matches high-end advertising standards. CRITICAL: PERFECT spelling and grammar - NO mistakes allowed.",
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
