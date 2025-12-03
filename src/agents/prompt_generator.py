"""
Prompt Generator Agent
Takes image + description and generates structured prompt for Google Nano Banana model
Enhanced with user-provided fonts, logo support, and flexible text placement
"""

import base64
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv

load_dotenv()

class PromptGeneratorAgent:
    """
    Prompt Generator Agent: Generates structured prompts for Google Nano Banana model
    Enhanced features:
    - User-provided fonts (any font name)
    - Company logo support
    - Flexible text placement
    - Optional pricing
    - Based on professional ad examples
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
    
    def _build_system_prompt(self, primary_font: Optional[str] = None, 
                            secondary_font: Optional[str] = None,
                            pricing_font: Optional[str] = None,
                            include_price: bool = True,
                            logo_path: Optional[str] = None) -> str:
        """
        Build system prompt with user-provided fonts and options
        
        Args:
            primary_font: User-provided primary font name
            secondary_font: User-provided secondary font name (optional)
            pricing_font: User-provided pricing font name (optional)
            include_price: Whether to include pricing information
            logo_path: Path to company logo (optional)
        """
        
        # Font instructions
        font_instructions = ""
        if primary_font:
            font_instructions += f"PRIMARY FONT: Use EXACTLY the font named '{primary_font}'. Do NOT substitute, modify, or use similar fonts. Use this exact font name only.\n"
        else:
            font_instructions += "PRIMARY FONT: Use a clean, professional serif or sans-serif font. Do not use generic or default fonts.\n"
        
        if secondary_font:
            font_instructions += f"SECONDARY FONT: Use EXACTLY the font named '{secondary_font}'. Do NOT substitute or modify.\n"
        elif primary_font:
            font_instructions += f"SECONDARY FONT: Use the same font as primary ({primary_font}) with different weight or size.\n"
        
        if include_price and pricing_font:
            font_instructions += f"PRICING FONT: Use EXACTLY the font named '{pricing_font}'. Do NOT substitute or modify.\n"
        elif include_price and primary_font:
            font_instructions += f"PRICING FONT: Use the same font as primary ({primary_font}) in bold weight.\n"
        
        # Logo instructions
        logo_instructions = ""
        if logo_path:
            logo_instructions = """
**LOGO PLACEMENT:**
- Place the company logo at the top-center or top-left of the image
- Logo should be clearly visible but not overpower the product
- Maintain logo's original colors and design - do not modify, distort, or redesign the logo
- Logo size: 150-200px width (relative to 1080px canvas)
- Position: 20-40px from top, centered horizontally or 40px from left
- Ensure text elements don't overlap with logo
"""
        
        # Price section (conditional) - use string replacement for placeholders
        pricing_font_name = pricing_font or (primary_font or "professional bold font")
        if include_price:
            price_section = f'''
            "pricing_display": {{
              "font": "{pricing_font_name}",
              "style": "Create a CONSOLIDATED PRICING BADGE. Use BOLD weight for clarity. Place in BOTTOM-RIGHT CORNER. Use simple, clean text design - NOT generic template badges. CRITICAL: PERFECT spelling and grammar.",
              "before_discount": {{
                "price": "[ORIGINAL PRICE]",
                "font": "{pricing_font_name}",
                "style": "Display with strike-through effect. Professional editing and elegant typography."
              }},
              "after_discount": {{
                "price": "[DISCOUNTED PRICE]",
                "font": "{pricing_font_name}",
                "style": "Display with BOLD weight for clear visibility. Professional editing and sophisticated typography."
              }},
              "placement": "BOTTOM-RIGHT CORNER in a consolidated badge."
            }},
            "limited_time_offer": {{
              "text": "[GENERATE LIMITED TIME OFFER TEXT]",
              "font": "{pricing_font_name}",
              "style": "INTEGRATE with pricing badge. Use simple, clean text design. Place above price within same container. CRITICAL: PERFECT spelling and grammar.",
              "placement": "INTEGRATED with pricing badge in bottom-right corner."
            }}'''
        else:
            price_section = '''
            "pricing_display": null,
            "limited_time_offer": null'''
        
        # Replace placeholders in font instructions
        font_instructions_processed = font_instructions.replace("[PRIMARY_FONT]", primary_font or "professional serif or sans-serif")
        font_instructions_processed = font_instructions_processed.replace("[SECONDARY_FONT]", secondary_font or (primary_font or "same as primary"))
        font_instructions_processed = font_instructions_processed.replace("[PRICING_FONT]", pricing_font or (primary_font or "professional bold font"))
        
        system_prompt = f"""You are an expert marketing prompt generator for Google's Nano Banana model.
Your task is to analyze a product image and description to create a structured JSON prompt
that will be used to generate PREMIUM Meta ad creatives that look like professional product photography.

CRITICAL QUALITY REQUIREMENTS:
- The final ad must look like professional product photography with soft natural lighting, subtle shadows, and realistic depth of field
- Do NOT use: flat backgrounds, bright saturated colors, heavy drop shadows, decorative borders, or template-style layouts
- Apply subtle color grading, soft shadows, natural highlights, and realistic depth of field blur
- PERFECT spelling and grammar - NO spelling mistakes allowed
- Use EXACTLY the fonts specified by the user - DO NOT substitute or modify font names
- DO NOT PRINT FONT NAMES AS TEXT IN THE GENERATED IMAGE - use the fonts, don't display the font names

{font_instructions_processed}

{logo_instructions}

You must generate a JSON prompt in this EXACT format:
{{
  "ad_type": "Meta ad Creative for the uploaded product",
  "model_name": "nano banana",
  "product_usage": "The provided product image has no background (transparent/white background). Create a realistic, natural background that complements the product. Option 1: Solid neutral background in light beige (#F5F5DC), light brown (#D2B48C), or off-white. No patterns, textures, or gradients. Option 2: Blurred natural setting (dining table, vanity, lifestyle context) with soft depth of field (40-50% blurred). Background should complement product colors. Do NOT modify, redesign, or alter the product itself - only add appropriate background and lighting.",
  "visual": {{
    "shot_type": "close-up",
    "highlight": "Showcase the product's unique texture, material, and key design features with sharp, clear visual focus.",
    "background": {{
      "style": "Create a solid neutral background (light beige #F5F5DC, light brown #D2B48C, or off-white) OR a blurred natural setting with soft depth of field. Background should be 40-50% blurred if using natural setting, maintaining context but keeping focus on product. Use warm, soft lighting. No patterns, textures, or gradients in solid backgrounds.",
      "props": "If using natural setting, include realistic, lifestyle-appropriate props (dining table, plates, fabric textures) that enhance the scene naturally. All props should look naturally placed and photographed, not artificially generated.",
      "contrast": "Create realistic depth with natural lighting, soft shadows, and subtle background blur. Lighting should be soft directional light from upper-left, creating gentle shadows on the right side. Avoid harsh, artificial lighting or overly perfect shadows."
    }},
    "appearance": "The final image must look like professional product photography with sophisticated editing, soft shadows, and realistic aesthetics. Apply subtle color grading, soft shadows (5-10px blur, 20% opacity), natural highlights, and realistic depth of field blur. The image should have the quality of a professional product photoshoot, not an AI illustration or template.",
    "lighting": "Use soft, even lighting with subtle shadows beneath product. Shadow: soft, diffused, 5-10px blur, 20% opacity, offset 3-5px downward. Product should appear slightly elevated, not flat on background. Lighting should look like it was captured with professional photography equipment."
  }},
  "product_placement": {{
    "position": "off-center",
    "horizontal": "60% from left OR 40% from left (not centered)",
    "vertical": "50% from top",
    "size": "65% of canvas height (700px for 1080px canvas)",
    "shadow": "soft, diffused, 5-10px blur, 20% opacity, offset 3-5px downward"
  }},
  "typography_and_layout": {{
    "style": "Clean, minimal design with strategic text placement. Text elements can be placed anywhere for optimal visual balance. All text must be artistically integrated into the composition as part of a professional graphic design layout, not as simple text overlays.",
    "visual_hierarchy": "Follow top-to-bottom hierarchy: Logo (if present) → Headline → Tagline → Body Text → Product → Features → CTA Button. Maintain 10% margin from all edges for text elements. Ensure text doesn't overlap with product unless intentional design choice.",
    "ratio": "1:1 (1080 x 1080 px)",
    "text_elements": [
      {{
        "type": "text",
        "text": "[GENERATE CATCHY HEADLINE - 2-6 WORDS, MEMORABLE AND IMPACTFUL]",
        "font": "{primary_font or 'professional serif or sans-serif'}",
        "placement": {{
          "position": "top-center",
          "x_offset": 0,
          "y_offset": 80,
          "alignment": "center"
        }},
        "style": {{
          "size": "xlarge",
          "weight": "bold",
          "color": "#2C2C2C",
          "transform": "uppercase"
        }},
        "hierarchy": "primary"
      }},
      {{
        "type": "text",
        "text": "[GENERATE CATCHY TAGLINE - MEMORABLE AND PERSUASIVE]",
        "font": "{secondary_font or primary_font or 'professional serif or sans-serif'}",
        "placement": {{
          "position": "top-center",
          "x_offset": 0,
          "y_offset": 140,
          "alignment": "center"
        }},
        "style": {{
          "size": "large",
          "weight": "regular",
          "color": "#2C2C2C",
          "transform": "none"
        }},
        "hierarchy": "secondary"
      }},
      {{
        "type": "features",
        "items": [
          {{"icon": "icon_name", "text": "[FEATURE 1]"}},
          {{"icon": "icon_name", "text": "[FEATURE 2]"}},
          {{"icon": "icon_name", "text": "[FEATURE 3]"}},
          {{"icon": "icon_name", "text": "[FEATURE 4]"}}
        ],
        "placement": {{
          "position": "bottom",
          "y_offset": -120
        }},
        "style": {{
          "layout": "horizontal",
          "spacing": "even"
        }}
      }},
      {{
        "type": "cta_button",
        "text": "[GENERATE CTA TEXT - e.g., 'SHOP NOW', 'Shop The Collection']",
        "placement": {{
          "position": "bottom-center",
          "y_offset": -40
        }},
        "style": {{
          "background_color": "#D2B48C",
          "text_color": "#2C2C2C",
          "border_radius": 8,
          "padding": "12px 32px"
        }}
      }}
    ],
{price_section}
  }},
  "branding": {{
    "logo": {{
      "enabled": {"true" if logo_path else "false"},
      "placement": {{
        "position": "top-center",
        "x_offset": 0,
        "y_offset": 20,
        "size": "medium"
      }},
      "style": {{
        "opacity": 1.0,
        "background": "transparent"
      }}
    }}
  }},
  "critical_mandates": [
    "**Absolute Rule:** Never change, redraw, or redesign the product. Use its real colors, structure, and features only.",
    "**Background:** Create solid neutral background (light beige #F5F5DC, light brown #D2B48C, or off-white) OR blurred natural setting with 40-50% depth of field blur. No patterns, textures, or gradients in solid backgrounds.",
    "**Product Positioning:** Position product off-center (60% from left OR 40% from left), at 50% from top, occupying 65% of canvas height. Add subtle shadow: soft, diffused, 5-10px blur, 20% opacity, offset 3-5px downward.",
    "**Typography:** Use EXACTLY the fonts specified. Do NOT substitute, modify, or use similar fonts. DO NOT print font names as text - use the fonts to display actual product text.",
    "**Text Placement:** Headline at top-center (80px from top), tagline below headline (140px from top), features at bottom (120px from bottom), CTA button at bottom-center (40px from bottom). Maintain 10% margin from edges.",
    "**Feature Icons:** Create 3-5 feature items with simple line-art icons and descriptive text. Arrange horizontally at bottom section. Icons: 40-50px, text: 16-20px font size. Even spacing across width.",
    "**CTA Button:** Rounded corners (8px), contrasting background color (#D2B48C or #2C2C2C), white or dark text, centered at bottom. Font size: 18-24px. Padding: 12px 32px.",
    "**Spelling:** CRITICAL - PERFECT spelling and grammar. AI image generation often has spelling errors - be extra careful. Review all text before including in JSON.",
    "**Output Format:** Generate final image in 1:1 aspect ratio (1080x1080 pixels). Product must be perfectly composed within this square frame.",
    "**Professional Quality:** The image should look like professional product photography, not AI-generated. Use realistic lighting, natural shadows, and authentic composition."
  ]
}}

Generate compelling headlines, taglines, feature descriptions, and CTA text based on the product analysis.
Make it specific, actionable, and tailored for Meta ad creative generation.

IMPORTANT: The input product image has no background. You must instruct the AI to CREATE a realistic, natural background that complements the product.

TEXT GENERATION REQUIREMENTS:
- Generate complete, compelling text for ALL text elements
- Headline: Create a catchy, one-liner headline (2-6 words) that is memorable and impactful
- Tagline: Create a catchy, one-liner tagline that is persuasive and memorable
- Features: Generate 3-5 product features with simple, clear descriptions
- CTA: Create compelling call-to-action text (e.g., "SHOP NOW", "Shop The Collection")
- Pricing: If included, generate both original and discounted prices with limited time offer text
- Ensure ALL text is complete and not cut off
- Use professional advertising copy that matches high-end product advertisements
- CRITICAL: Ensure ALL text has correct spelling and grammar - AI image generation often has spelling errors
- Make headlines and taglines catchy, memorable one-liners that stick in the mind

CRITICAL: You must return a complete, valid JSON object. Ensure all brackets, braces, and quotes are properly closed. The JSON must be parseable and complete.

**ABSOLUTELY CRITICAL: DO NOT PRINT FONT NAMES AS TEXT IN THE GENERATED IMAGE.**
**The font field specifies which font to USE, not what text to DISPLAY.**
**Generate actual product headlines, taglines, and text - NOT font names.**"""
        
        return system_prompt
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 for API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def generate_prompt(self, image_path: str, description: str, 
                       user_inputs: Optional[Dict[str, Any]] = None,
                       primary_font: Optional[str] = None,
                       secondary_font: Optional[str] = None,
                       pricing_font: Optional[str] = None,
                       include_price: bool = True,
                       logo_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate structured prompt based on image and description
        
        Args:
            image_path: Path to the product image
            description: Product description
            user_inputs: Optional user inputs for target audience, price, etc.
            primary_font: User-provided primary font name
            secondary_font: User-provided secondary font name (optional)
            pricing_font: User-provided pricing font name (optional)
            include_price: Whether to include pricing information
            logo_path: Path to company logo (optional)
        
        Returns:
            Dictionary containing the generated prompt and metadata
        """
        try:
            # Build system prompt with user options
            system_prompt = self._build_system_prompt(
                primary_font=primary_font,
                secondary_font=secondary_font,
                pricing_font=pricing_font,
                include_price=include_price,
                logo_path=logo_path
            )
            
            # Encode image
            base64_image = self.encode_image(image_path)
            
            # Prepare user message with font information
            font_info = []
            if primary_font:
                font_info.append(f"Primary Font: {primary_font}")
            if secondary_font:
                font_info.append(f"Secondary Font: {secondary_font}")
            if include_price and pricing_font:
                font_info.append(f"Pricing Font: {pricing_font}")
            
            font_text = "\n".join(font_info) if font_info else "No specific fonts provided - use professional fonts"
            
            # Prepare messages for Gemini
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=[
                    {
                        "type": "text",
                        "text": f"""
                        Product Description: {description}
                        
                        User Inputs: {user_inputs or "None provided"}
                        
                        Font Information:
                        {font_text}
                        
                        Please analyze this product image and generate a structured prompt for Google's Nano Banana model.
                        The product image has no background, so you must instruct the AI to CREATE a realistic, natural background that complements the product.
                        
                        CRITICAL REQUIREMENTS:
                        - Use EXACTLY the fonts specified above. Do NOT substitute or modify font names.
                        - Generate complete, compelling text for ALL text elements
                        - Headline: Create a catchy, one-liner headline (2-6 words) that is memorable and impactful
                        - Tagline: Create a catchy, one-liner tagline that is persuasive and memorable
                        - Features: Generate 3-5 product features with simple, clear descriptions and appropriate icon suggestions
                        - CTA: Create compelling call-to-action text
                        - Ensure ALL text has correct spelling and grammar - AI image generation often has spelling errors
                        - Make headlines and taglines catchy, memorable one-liners that stick in the mind
                        - Place text elements strategically based on product analysis and modern advertising principles
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
                    "user_inputs": user_inputs,
                    "primary_font": primary_font,
                    "secondary_font": secondary_font,
                    "pricing_font": pricing_font,
                    "include_price": include_price,
                    "logo_path": logo_path
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
