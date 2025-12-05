"""
Prompt Generator Agent
Takes image + description and generates structured prompt for Google Nano Banana model
Enhanced with user-provided fonts, logo support, and flexible text placement
"""

import base64
import json
import re
import random
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
        # Use specific key for prompt generation, fall back to general key
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY_PROMPT") or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY_PROMPT or GOOGLE_API_KEY environment variable.")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-image-preview",
            google_api_key=self.api_key,
            temperature=0.9,  # Higher temperature for more creative variety
            max_tokens=3000  # Increased to prevent JSON truncation
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
        
        # Add randomization for variety in each generation
        background_options = [
            "warm beige gradient transitioning to soft cream, reminiscent of high-end furniture catalogs",
            "cool gray concrete texture with subtle imperfections for industrial-chic aesthetic",
            "natural oak wood grain surface with soft golden hour lighting",
            "luxurious marble surface with delicate veining in cream and gray tones",
            "soft linen fabric texture in muted earth tones with gentle folds",
            "minimalist pure white with dramatic directional shadows",
            "dark charcoal moody background with single spotlight creating drama",
            "soft terracotta clay surface with Mediterranean warmth",
            "brushed metal surface with subtle reflections for modern tech aesthetic",
            "natural stone texture in warm sandstone tones"
        ]
        
        layout_options = [
            "asymmetric with product positioned at golden ratio (61.8% from left), text balancing the composition",
            "centered product with elegant text framing above and below in classic luxury style",
            "dynamic diagonal composition with product on lower-right, text flowing from upper-left",
            "minimalist with product dominating 70% of frame, subtle text elements",
            "editorial style with product on left third, generous text space on right",
            "modern split-screen feel with clear zones for product and messaging"
        ]
        
        mood_options = [
            "warm and inviting, like a cozy home lifestyle brand",
            "cool and sophisticated, like a premium tech company",
            "earthy and organic, like an artisan craft brand",
            "bold and confident, like a luxury fashion house",
            "serene and minimal, like a Scandinavian design brand",
            "rich and opulent, like a heritage luxury brand"
        ]
        
        selected_background = random.choice(background_options)
        selected_layout = random.choice(layout_options)
        selected_mood = random.choice(mood_options)
        
        system_prompt = f"""You are an expert creative director at a top advertising agency.
Your task is to create a structured JSON prompt for generating PREMIUM Meta ad creatives.
The output should look like it was designed by a professional team at agencies like Ogilvy, Wieden+Kennedy, or Droga5.

CREATIVE DIRECTION FOR THIS AD:
- BACKGROUND STYLE: {selected_background}
- LAYOUT APPROACH: {selected_layout}  
- OVERALL MOOD: {selected_mood}

PROFESSIONAL QUALITY STANDARDS:
- Study reference: Apple product ads, Dyson campaigns, Bang & Olufsen visuals, Aesop packaging
- The ad must look like it cost $10,000+ to produce - premium, polished, intentional
- Every element should feel deliberately placed by a skilled designer
- Use sophisticated color grading - not flat or oversaturated
- Typography should be perfectly balanced with proper kerning and hierarchy
- Negative space is crucial - let the design breathe
- Shadows should be soft, realistic, and grounded (not floating)
- Lighting should feel natural yet cinematic
- AVOID: Template looks, clipart feel, generic stock photo aesthetic, busy designs
- PERFECT spelling and grammar - NO spelling mistakes allowed

**ABSOLUTELY CRITICAL - FONT USAGE:**
- The "font" field in JSON is a TECHNICAL SPECIFICATION for which font to USE, NOT text to DISPLAY
- NEVER print the font name as visible text in the image
- Generate actual product text (headlines, taglines, etc.) - NOT font names
- Example: If font is "Tan Pearl" and product is a wooden organizer, use Tan Pearl font to render "ORGANIZE ARTFULLY" - DO NOT display "Tan Pearl" as text

{font_instructions_processed}

{logo_instructions}

You must generate a JSON prompt in this EXACT format:
{{
  "ad_type": "Meta ad Creative for the uploaded product",
  "model_name": "nano banana",
  "creative_direction": {{
    "background_style": "{selected_background}",
    "layout_approach": "{selected_layout}",
    "mood": "{selected_mood}"
  }},
  "product_usage": "The provided product image has no background. Create the background following this direction: {selected_background}. Do NOT modify, redesign, or alter the product itself - only add appropriate background and lighting that matches the creative direction.",
  "visual": {{
    "shot_type": "hero product shot with cinematic quality",
    "highlight": "Showcase the product's unique texture, material, and key design features. Make it look desirable and premium.",
    "background": {{
      "style": "{selected_background}",
      "execution": "Create depth and atmosphere. The background should support the product, not compete with it. Use subtle gradients, texture, or environmental context as specified in the creative direction.",
      "props": "Only include props if they enhance the lifestyle context. Each prop should feel intentional and premium. Less is more."
    }},
    "appearance": "The final image must look like it was shot by a professional photographer and art-directed by a creative director. Think Apple product shots, Dyson campaigns, luxury brand catalogs. No template feel, no stock photo aesthetic.",
    "lighting": "Cinematic, intentional lighting that creates mood and dimension. Soft key light with subtle fill. Shadows should be realistic and grounded. The lighting should match the mood: {selected_mood}"
  }},
  "product_placement": {{
    "layout_direction": "{selected_layout}",
    "positioning": "Follow the layout direction above. Product should be the hero but placement should feel dynamic and intentional, not centered and static.",
    "size": "Product should dominate visually but leave room for typography. Scale appropriately based on layout.",
    "shadow": "Realistic, grounded shadow that matches the lighting direction. Not floating, not too harsh, not too soft."
  }},
  "typography_and_layout": {{
    "style": "Premium typography that matches the mood: {selected_mood}. Every text element should feel deliberately designed. Use proper typographic hierarchy.",
    "visual_hierarchy": "Clear hierarchy: Headline (largest, boldest) → Tagline (supporting) → Features (if included) → Price/CTA (action-driving). Balance with product placement.",
    "ratio": "MANDATORY 1:1 SQUARE (1080 x 1080 px) - Width MUST equal Height",
    "text_elements": [
      {{
        "type": "text",
        "text": "[GENERATE A UNIQUE HEADLINE SPECIFIC TO THIS PRODUCT - Based on the product description, create a 2-6 word headline that: 1) Highlights what makes THIS specific product special, 2) Speaks directly to the target audience's desires, 3) Is NOT generic like 'Elegance Unveiled' or 'Timeless Beauty' - make it SPECIFIC to this product category and features, 4) Could only work for THIS type of product]",
        "font": "{primary_font or 'professional serif or sans-serif'}",
        "headline_examples_by_category": {{
          "home_decor": ["ARTISAN CRAFTED", "HOME REIMAGINED", "CURATED LIVING", "HANDMADE HERITAGE"],
          "kitchenware": ["KITCHEN ELEVATED", "CULINARY CRAFT", "COOK WITH SOUL", "TASTE PERFECTED"],
          "photo_frames": ["MEMORIES FRAMED", "MOMENTS PRESERVED", "CAPTURE FOREVER", "STORIES DISPLAYED"],
          "organizers": ["DECLUTTER BEAUTIFULLY", "ORDER MEETS ART", "ORGANIZED ELEGANCE", "TIDY IN STYLE"],
          "luxury_gifts": ["GIFT EXTRAORDINARY", "UNWRAP LUXURY", "PRESENT PERFECTION", "TREASURED GIVING"]
        }},
        "instruction": "Generate a headline that is SPECIFIC to this product type. Do NOT use generic phrases. Think about what problem this product solves or what emotion it evokes for the target audience.",
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
        "text": "[GENERATE A UNIQUE TAGLINE SPECIFIC TO THIS PRODUCT AND TARGET AUDIENCE - Create a tagline that: 1) Directly addresses the target audience's pain point or aspiration, 2) Mentions or implies the product's key benefit, 3) Feels personal and specific, NOT generic marketing speak, 4) Would make the target audience think 'this is for me']",
        "font": "{secondary_font or primary_font or 'professional serif or sans-serif'}",
        "tagline_examples_by_audience": {{
          "home_decor_enthusiasts": ["Transform your space, express your soul", "Where design meets your story", "Your home, your masterpiece"],
          "luxury_buyers": ["For those who appreciate the finer things", "Crafted for the discerning eye", "Excellence you can see and feel"],
          "gift_givers": ["Give something they'll treasure forever", "The gift that speaks volumes", "Make moments unforgettable"],
          "busy_professionals": ["Simplify beautifully", "Order without compromise", "Efficiency meets elegance"]
        }},
        "instruction": "Generate a tagline that speaks DIRECTLY to the target audience. What do they want? What problem does this solve? Make them feel understood.",
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
    "**MANDATORY ASPECT RATIO - FIRST PRIORITY:** Generate the image in EXACTLY 1:1 aspect ratio (SQUARE format). Output dimensions MUST be 1080x1080 pixels. Width MUST equal height. Do NOT generate landscape or portrait images. This is a Meta ad creative requirement.",
    "**Absolute Rule:** Never change, redraw, or redesign the product. Use its real colors, structure, and features only.",
    "**Background:** Create solid neutral background (light beige #F5F5DC, light brown #D2B48C, or off-white) OR blurred natural setting with 40-50% depth of field blur. No patterns, textures, or gradients in solid backgrounds.",
    "**Product Positioning:** Position product off-center (60% from left OR 40% from left), at 50% from top, occupying 65% of canvas height. Add subtle shadow: soft, diffused, 5-10px blur, 20% opacity, offset 3-5px downward.",
    "**Typography - CRITICAL FONT USAGE RULE:** The 'font' field in each text element is a TECHNICAL SPECIFICATION telling you which font to USE for rendering. It is NOT text to display. NEVER print font names like 'Tan Pearl', 'Calgary', or 'RoxboroughCF' as visible text in the image. Generate UNIQUE product headlines based on what the product actually is. Example: For a photo frame, use the font to render 'FRAME YOUR STORY' - do NOT display the font name as text.",
    "**Text Placement:** Headline at top-center (80px from top), tagline below headline (140px from top), features at bottom (120px from bottom), CTA button at bottom-center (40px from bottom). Maintain 10% margin from edges.",
    "**Feature Icons:** Create 3-5 feature items with simple line-art icons and descriptive text. Arrange horizontally at bottom section. Icons: 40-50px, text: 16-20px font size. Even spacing across width.",
    "**CTA Button:** Rounded corners (8px), contrasting background color (#D2B48C or #2C2C2C), white or dark text, centered at bottom. Font size: 18-24px. Padding: 12px 32px.",
    "**Spelling:** CRITICAL - PERFECT spelling and grammar. AI image generation often has spelling errors - be extra careful. Review all text before including in JSON.",
    "**Output Format - SQUARE IMAGE:** Generate final image in 1:1 aspect ratio (1080x1080 pixels). The image MUST be square. Product must be perfectly composed within this square frame.",
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

        CRITICAL JSON REQUIREMENTS:
        - You must return a complete, valid JSON object
        - Ensure all brackets, braces, and quotes are properly closed
        - Escape all quotes inside string values using backslash: \"
        - Do not include newlines or unescaped special characters in string values
        - The JSON must be parseable and complete
        - If text contains quotes, escape them: \"example text\"
        - If text contains newlines, use \\n or keep on single line
        - Ensure all string values are properly quoted and escaped
        
        **ABSOLUTELY CRITICAL - FONT NAME DISPLAY PROHIBITION:**
        **NEVER PRINT FONT NAMES AS TEXT IN THE GENERATED IMAGE.**
        **The "font" field in JSON is a TECHNICAL SPECIFICATION - it tells you which font to USE for rendering.**
        **It is NOT text content to display.**
        **Examples of WRONG behavior:**
        **  - Displaying "Tan Pearl" as text in the image**
        **  - Displaying "Calgary" as text in the image**
        **  - Displaying "RoxboroughCF" as text in the image**
        **Examples of CORRECT behavior (product-specific headlines):**
        **  - Wooden organizer: Using font to render "DECLUTTER IN STYLE" or "ORGANIZE ARTFULLY"**
        **  - Photo frame: Using font to render "FRAME YOUR STORY" or "MEMORIES DISPLAYED"**
        **  - Kitchen item: Using font to render "COOK WITH SOUL" or "KITCHEN ELEVATED"**
        **  - Pricing: Using font to render "Rs. 1899"**
        **Generate actual product headlines, taglines, pricing, and feature text - NOT font names.**
        **The font name should ONLY exist in the JSON "font" field as a specification, NEVER as displayed text.**"""
        
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
                        
                        CRITICAL REQUIREMENTS FOR UNIQUE TEXT GENERATION:
                        
                        **HEADLINE MUST BE UNIQUE TO THIS PRODUCT:**
                        - Analyze the product description: "{description}"
                        - Analyze the target audience: "{user_inputs.get('target_audience', 'general') if user_inputs else 'general'}"
                        - Create a headline that could ONLY work for this specific product
                        - DO NOT use generic phrases like "Elegance Unveiled", "Timeless Beauty", "Premium Quality"
                        - Instead, reference: the product material, its function, the lifestyle it enables, or the problem it solves
                        - Examples: For a wooden organizer → "DECLUTTER IN STYLE" or "ORGANIZE ARTFULLY"
                        - Examples: For a photo frame → "FRAME YOUR STORY" or "MEMORIES DISPLAYED"
                        - The headline should make someone instantly understand what the product is about
                        
                        **TAGLINE MUST SPEAK TO THE TARGET AUDIENCE:**
                        - Who is the target audience? Think about their desires, pain points, aspirations
                        - Create a tagline that makes them think "this is exactly what I need"
                        - Reference their lifestyle, values, or the transformation the product offers
                        - DO NOT use vague phrases like "Crafted Perfection" or "Quality You Deserve"
                        - Be SPECIFIC about the benefit or emotion
                        
                        **OTHER REQUIREMENTS:**
                        - Use EXACTLY the fonts specified above
                        - Features: Generate 3-5 product-specific features based on the actual product
                        - CTA: Create compelling call-to-action text
                        - Ensure ALL text has correct spelling and grammar
                        - Place text elements strategically based on the layout direction
                        
                        **ABSOLUTELY CRITICAL - FONT NAME PROHIBITION (READ THIS CAREFULLY):**
                        - NEVER use font names (like "Tan Pearl", "Calgary", "RoxboroughCF") as the actual text content
                        - NEVER use font names as product names, collection names, or any displayed text
                        - The "font" field is a specification - it tells which font to USE, not what to DISPLAY
                        - Generate UNIQUE product-related text based on what the product actually is
                        - Use the specified fonts to render that text, but never display the font names themselves
                        - Example: For an organizer product with font "Tan Pearl", generate "ORGANIZE ARTFULLY" and use Tan Pearl font to render it
                        - Example: For a photo frame product, generate "FRAME YOUR STORY" or "MEMORIES DISPLAYED"
                        - WRONG: Putting "Tan Pearl" or any font name as text in the image
                        - WRONG: Using generic phrases like "Elegance Unveiled" for every product
                        - CORRECT: Creating a headline specific to THIS product type and the target audience
                        - DO NOT create a product name or collection name that matches the font name
                        - If you see a font name in the font field, use that font but generate DIFFERENT text content
                        - The text in "text" fields should NEVER match or contain the font name from the "font" field
                        
                        CRITICAL JSON FORMATTING:
                        - Escape all quotes in text values: use \" instead of "
                        - Keep all text on single lines (no actual newlines in JSON strings)
                        - Ensure all brackets and braces are properly closed
                        - Return complete, valid JSON that can be parsed without errors
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
            
            # Post-process to remove font names from text fields
            prompt_text = self._remove_font_names_from_text(prompt_text, primary_font, secondary_font, pricing_font)
            
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
    
    def _remove_font_names_from_text(self, prompt_text: str, primary_font: Optional[str], 
                                     secondary_font: Optional[str], 
                                     pricing_font: Optional[str]) -> str:
        """
        Post-process the generated prompt to remove font names from text fields.
        This prevents font names from appearing as displayed text in the final image.
        """
        # Collect all font names to check for
        font_names = []
        if primary_font:
            font_names.append(primary_font)
        if secondary_font:
            font_names.append(secondary_font)
        if pricing_font:
            font_names.append(pricing_font)
        
        if not font_names:
            return prompt_text
        
        # Try to parse JSON and clean it
        try:
            # Clean markdown code blocks
            clean_prompt = prompt_text
            if clean_prompt.startswith('```json'):
                clean_prompt = clean_prompt[7:]
            elif clean_prompt.startswith('```'):
                clean_prompt = clean_prompt[3:]
            if clean_prompt.endswith('```'):
                clean_prompt = clean_prompt[:-3]
            clean_prompt = clean_prompt.strip()
            
            # Find JSON object
            json_start = clean_prompt.find('{')
            json_end = clean_prompt.rfind('}')
            
            if json_start != -1 and json_end != -1:
                json_str = clean_prompt[json_start:json_end+1]
                prefix = clean_prompt[:json_start]
                suffix = clean_prompt[json_end+1:]
                
                # Parse JSON
                prompt_json = json.loads(json_str)
                
                # Function to recursively clean text fields
                def clean_text_fields(obj, font_names_list):
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            if key == "text" and isinstance(value, str):
                                # Check if text contains any font name
                                for font_name in font_names_list:
                                    # Case-insensitive check
                                    if font_name.lower() in value.lower():
                                        # Replace font name with generic product text
                                        # Simply remove the font name from the text - don't replace with generic phrases
                                        # The AI should have generated unique text; we just need to remove any accidental font name inclusion
                                        value = re.sub(re.escape(font_name), "", value, flags=re.IGNORECASE).strip()
                                        # Clean up any double spaces left behind
                                        value = re.sub(r'\s+', ' ', value).strip()
                                        obj[key] = value
                            elif key == "items" and isinstance(value, list):
                                # Handle feature items
                                for item in value:
                                    if isinstance(item, dict) and "text" in item:
                                        for font_name in font_names_list:
                                            if font_name.lower() in item["text"].lower():
                                                # Remove font name from feature text
                                                item["text"] = re.sub(re.escape(font_name), "", item["text"], flags=re.IGNORECASE).strip()
                            else:
                                clean_text_fields(value, font_names_list)
                    elif isinstance(obj, list):
                        for item in obj:
                            clean_text_fields(item, font_names_list)
                
                # Clean the JSON
                clean_text_fields(prompt_json, font_names)
                
                # Reconstruct the prompt
                cleaned_json_str = json.dumps(prompt_json, indent=2)
                return prefix + cleaned_json_str + suffix
            else:
                # If JSON parsing fails, do simple string replacement as fallback
                cleaned = prompt_text
                for font_name in font_names:
                    # Only replace if it's clearly being used as text (not in font field)
                    # This is a heuristic - look for font name in quotes or as standalone text
                    pattern = rf'["\']\s*{re.escape(font_name)}\s*["\']'
                    cleaned = re.sub(pattern, '"PRODUCT TEXT"', cleaned, flags=re.IGNORECASE)
                return cleaned
                
        except (json.JSONDecodeError, Exception) as e:
            # If JSON parsing fails, do simple string replacement as fallback
            cleaned = prompt_text
            for font_name in font_names:
                # Try to replace font names that appear in text fields (heuristic)
                # Look for patterns like "text": "Tan Pearl" or similar
                pattern = rf'"text"\s*:\s*["\']\s*{re.escape(font_name)}\s*["\']'
                replacement = '"text": "PRODUCT HEADLINE"'
                cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
            return cleaned
    
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
