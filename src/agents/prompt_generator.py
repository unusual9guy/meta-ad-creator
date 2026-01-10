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
from langchain_core.messages import HumanMessage, SystemMessage
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
            temperature=0.95,  # Higher temperature for more creative variety
            max_tokens=3000  # Increased to prevent JSON truncation
        )
    
    def _build_system_prompt(self, font_styles: Optional[Dict[str, str]] = None,
                            include_price: bool = True,
                            logo_path: Optional[str] = None,
                            promotion_text: Optional[str] = None,
                            before_price: Optional[str] = None,
                            after_price: Optional[str] = None) -> str:
        """
        Build system prompt with auto-detected font styles and options
        
        Args:
            font_styles: Dictionary with font style descriptions for headline, tagline, cta, price
            include_price: Whether to include pricing information
            logo_path: Path to company logo (optional)
            promotion_text: Promotion text (e.g., "30% winter sale") (optional)
            before_price: Original price text (e.g., "Rs. 2499") (optional)
            after_price: Discounted/final price text (e.g., "Rs. 1749") (optional)
        """
        
        # Get font styles or use defaults
        if not font_styles:
            font_styles = {
                "headline": "Professional, well-balanced serif or sans-serif with clear hierarchy",
                "tagline": "Clean, readable sans-serif with balanced proportions",
                "cta": "Medium-weight sans-serif, clear and confident",
                "price": "Clear, modern sans-serif with high legibility"
            }
        
        headline_style = font_styles.get("headline", "Professional serif or sans-serif")
        tagline_style = font_styles.get("tagline", "Clean, readable sans-serif")
        cta_style = font_styles.get("cta", "Medium-weight sans-serif")
        price_style = font_styles.get("price", "Clear, modern sans-serif")
        
        # Font instructions using descriptive styles (not specific font names)
        font_instructions = f"""
**TYPOGRAPHY SPECIFICATIONS - CRITICAL:**
Use typography that matches these style descriptions. The AI should render text in fonts that match these characteristics:

- **HEADLINE TYPOGRAPHY:** {headline_style}
- **TAGLINE TYPOGRAPHY:** {tagline_style}
- **CTA BUTTON TYPOGRAPHY:** {cta_style}
"""
        if include_price:
            font_instructions += f"- **PRICE TYPOGRAPHY:** {price_style}\n"
        
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
        
        # Price section (conditional) - use actual before/after prices if provided
        if include_price:
            before_price_text = (before_price or "[ORIGINAL PRICE]").strip()
            after_price_text = (after_price or "[DISCOUNTED PRICE]").strip()
            # Define limited time offer text outside f-string to avoid backslash issues
            if promotion_text:
                limited_time_text = '[PROMOTION IS ALREADY IN HEADLINE - DO NOT DUPLICATE HERE. Leave this field empty or use generic text like "Limited Time Offer" if needed]'
            else:
                limited_time_text = '[GENERATE LIMITED TIME OFFER TEXT]'
            price_section = f'''
            "pricing_display": {{
              "typography_style": "{price_style}",
              "style": "Create a clean, modern HORIZONTAL PRICE STRIP along the bottom of the ad. The strip should span most of the width with subtle rounded corners. Keep it minimal and premium - no bulky badge or sticker look. Use BOLD weight for clarity.",
              "before_discount": {{
                "price": "{before_price_text}",
                "typography_style": "{price_style}",
                "style": "Display with a subtle strike-through effect on the left side of the strip. Use refined, elegant typography."
              }},
              "after_discount": {{
                "price": "{after_price_text}",
                "typography_style": "{price_style}",
                "style": "Display prominently on the right side of the strip with BOLD weight for clear visibility. Professional, sophisticated typography."
              }},
              "placement": "BOTTOM EDGE - FULL-WIDTH HORIZONTAL STRIP, aligned center, sitting just above the bottom margin."
            }},
            "limited_time_offer": {{
              "text": "{limited_time_text}",
              "typography_style": "{price_style}",
              "style": "If used, integrate this text INSIDE the same horizontal price strip, in smaller type above or beside the prices. Keep it subtle and premium. CRITICAL: PERFECT spelling and grammar.",
              "placement": "INTEGRATED inside the same bottom horizontal price strip."
            }}'''
        else:
            price_section = '''
            "pricing_display": null,
            "limited_time_offer": null'''
        
        # Font instructions are already complete, no placeholders to replace
        font_instructions_processed = font_instructions
        
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
        
        # Build critical mandates list with conditional pricing instruction
        if include_price:
            pricing_mandate = "**Pricing Display:** Create a consolidated pricing badge in the bottom-right corner if pricing is included."
        else:
            pricing_mandate = "**Pricing Display:** DO NOT include any pricing information, price tags, discount badges, or pricing elements in the image. The user has explicitly chosen NOT to include pricing. Completely exclude all pricing-related visual elements."
        
        # Build headline instruction text based on whether promotion is included
        if promotion_text:
            promotion_text_verbatim = promotion_text.upper()
            headline_instruction = (
                f'[GENERATE A UNIQUE HEADLINE SPECIFIC TO THIS PRODUCT - Based on the product description, create a compelling headline that: '
                f'1) Highlights what makes THIS specific product special, '
                f'2) Speaks directly to the target audience\'s desires, '
                f'3) Is NOT generic like \\\'Elegance Unveiled\\\' or \\\'Timeless Beauty\\\' - make it SPECIFIC to this product category and features, '
                f'4) Could only work for THIS type of product, '
                f'5) **CRITICAL: MUST INCLUDE THE PROMOTION TEXT IN THE HEADLINE VERBATIM** - Integrate the promotion text "{promotion_text_verbatim}" smoothly and naturally into the headline. '
                f'**ABSOLUTELY CRITICAL RULES FOR PROMOTION TEXT:** '
                f'- Use the EXACT, COMPLETE promotion text provided - do NOT abbreviate, truncate, or shorten ANY words. '
                f'- If the text is "30% Winter Sale", you MUST use "30% WINTER SALE" (full text with all words) - NEVER "30% W SALE" or any abbreviation. '
                f'- NEVER abbreviate "Winter" to "W" or "Sale" to "S" - keep every word fully spelled out. '
                f'- **DO NOT use the pipe symbol "|" as a separator.** '
                f'- Blend the promotion smoothly using a dash "-", a comma ",", or natural phrasing without separators. '
                f'Examples of GOOD integration: "ILLUMINATE WITH GRACE - 30% WINTER SALE" or "ELEVATE YOUR SPACE, 30% WINTER SALE" or "PREMIUM QUALITY 30% WINTER SALE". '
                f'Examples of BAD integration: "ELEVATE YOUR SPACE | 30% W SALE" (pipe + abbreviation - NOT allowed). '
                f'The promotion must flow naturally within the headline text and must be fully spelled out with ALL words intact.]'
            )
        else:
            headline_instruction = (
                '[GENERATE A UNIQUE HEADLINE SPECIFIC TO THIS PRODUCT - Based on the product description, create a 2-6 word headline that: '
                '1) Highlights what makes THIS specific product special, '
                '2) Speaks directly to the target audience\'s desires, '
                '3) Is NOT generic like \'Elegance Unveiled\' or \'Timeless Beauty\' - make it SPECIFIC to this product category and features, '
                '4) Could only work for THIS type of product]'
            )
        
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
        "text": "{headline_instruction}",
        "typography_style": "{headline_style}",
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
        "typography_style": "{tagline_style}",
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
        "typography_style": "{cta_style}",
        "placement": {{
          "position": "bottom-center",
          "y_offset": {120 if include_price else 80}
        }},
        "style": {{
          "background_color": "#D2B48C",
          "text_color": "#2C2C2C",
          "border_radius": 8,
          "padding": "12px 32px"
        }},
        "instruction": "Place the CTA button BELOW the product with sufficient spacing. Ensure it does NOT overlap with the product. Position it at least 80-120px from the bottom edge, depending on whether pricing is included. The button should be clearly separated from the product. Use the specified typography style for the button text."
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
    "**Text Placement:** Headline at top-center (80px from top), tagline below headline (140px from top), features at bottom (120px from bottom), CTA button at bottom-center with proper spacing from product. Maintain 10% margin from edges.",
    "**Feature Icons:** Create 3-5 feature items with simple line-art icons and descriptive text. Arrange horizontally at bottom section. Icons: 40-50px, text: 16-20px font size. Even spacing across width.",
    "**CTA Button:** Rounded corners (8px), contrasting background color (#D2B48C or #2C2C2C), white or dark text, centered at bottom. Font size: 18-24px. Padding: 12px 32px. **CRITICAL: Position the CTA button BELOW the product with at least 60-80px gap to prevent overlap. The button must be clearly separated from the product and not overlap with it.**",
    "{pricing_mandate}",
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
    
    def generate_prompt(self, image_path: str, 
                       product_persona: Optional[Dict[str, Any]] = None,
                       description: Optional[str] = None,
                       user_inputs: Optional[Dict[str, Any]] = None,
                       include_price: bool = True,
                       logo_path: Optional[str] = None,
                       promotion_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate structured prompt based on product persona
        
        Args:
            image_path: Path to the product image
            product_persona: Structured product persona from Agent 1 (includes auto-detected font styles)
            description: Product description (legacy, used if product_persona not provided)
            user_inputs: Optional user inputs (legacy, used if product_persona not provided)
            include_price: Whether to include pricing information
            logo_path: Path to company logo (optional)
            promotion_text: Promotion text (e.g., "30% winter sale") (optional)
        
        Returns:
            Dictionary containing the generated prompt and metadata
        """
        try:
            # Extract information from product_persona if provided, otherwise use legacy parameters
            before_price = None
            after_price = None
            if product_persona:
                ai_analysis = product_persona.get("ai_analysis", {})
                user_data = product_persona.get("user_inputs", {})
                
                product_description = user_data.get("usp", "") or ai_analysis.get("raw_analysis", "") or description or ""
                target_audience = user_data.get("target_audience", "")
                product_name = user_data.get("product_name", "")
                promotion_data = user_data.get("promotion", {})
                
                # Use promotion text and pricing from persona if available
                if promotion_data.get("included", False):
                    # Only set promotion_text if user didn't provide one in the UI
                    if not promotion_text and promotion_data.get("percentage"):
                        promotion_text = f"{promotion_data.get('percentage', 0)}% OFF"
                # Pricing (before/after) is always taken from persona if present
                before_price = promotion_data.get("before_price") or None
                after_price = promotion_data.get("after_price") or None
                
                # Extract font styles from AI analysis
                font_styles = ai_analysis.get('font_styles', None)
                
                # Build comprehensive product context
                product_context = f"""
PRODUCT ANALYSIS (from AI):
- Product Type: {ai_analysis.get('product_type', 'Not specified')}
- Materials: {', '.join(ai_analysis.get('materials', [])) if ai_analysis.get('materials') else 'Not specified'}
- Key Features: {', '.join(ai_analysis.get('features', [])) if ai_analysis.get('features') else 'Not specified'}
- Style: {ai_analysis.get('style', 'Not specified')}
- Use Cases: {', '.join(ai_analysis.get('suggested_use_cases', [])) if ai_analysis.get('suggested_use_cases') else 'Not specified'}

USER PROVIDED INFORMATION:
- Product Name: {product_name}
- USP/Use Case: {user_data.get('usp', 'Not provided')}
- Target Audience: {target_audience}
- Additional Comments: {user_data.get('additional_comments', 'None')}
"""
            else:
                font_styles = None  # Will use defaults
                # Legacy mode: use description and user_inputs
                product_description = description or ""
                target_audience = user_inputs.get('target_audience', 'general') if user_inputs else 'general'
                product_name = ""
                product_context = f"""
Product Description: {product_description}
Target Audience: {target_audience}
User Inputs: {user_inputs or "None provided"}
"""
            
            # Build system prompt with auto-detected font styles
            system_prompt = self._build_system_prompt(
                font_styles=font_styles,
                include_price=include_price,
                logo_path=logo_path,
                promotion_text=promotion_text,
                before_price=before_price,
                after_price=after_price
            )
            
            # Encode image
            base64_image = self.encode_image(image_path)
            
            # Prepare user message with font style information
            if font_styles:
                font_text = f"""Typography Styles (auto-detected based on product style):
- Headline: {font_styles.get('headline', 'Professional serif')[:80]}...
- Tagline: {font_styles.get('tagline', 'Clean sans-serif')[:80]}...
- CTA: {font_styles.get('cta', 'Medium-weight sans-serif')[:80]}...
- Price: {font_styles.get('price', 'Clear sans-serif')[:80]}..."""
            else:
                font_text = "Typography: Use professional, balanced typography appropriate for premium product advertising"
            
            # Prepare promotion information
            promotion_info = ""
            if promotion_text and include_price:
                promotion_info = f"\nPromotion: {promotion_text}"
            
            # Prepare messages for Gemini
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=[
                    {
                        "type": "text",
                        "text": f"""
{product_context}
                        
Font Information:
{font_text}
{promotion_info}
                        
                        Please analyze this product image and generate a structured prompt for Google's Nano Banana model.
                        The product image has no background, so you must instruct the AI to CREATE a realistic, natural background that complements the product.

CRITICAL REQUIREMENTS FOR UNIQUE TEXT GENERATION:

                        **HEADLINE MUST BE UNIQUE TO THIS PRODUCT:**
                        - Analyze the product information above
                        - Analyze the target audience: "{target_audience}"
                        - Create a headline that could ONLY work for this specific product
                        - DO NOT use generic phrases like "Elegance Unveiled", "Timeless Beauty", "Premium Quality"
                        - Instead, reference: the product material, its function, the lifestyle it enables, or the problem it solves
                        - Examples: For a wooden organizer → "DECLUTTER IN STYLE" or "ORGANIZE ARTFULLY"
                        - Examples: For a photo frame → "FRAME YOUR STORY" or "MEMORIES DISPLAYED"
                        - The headline should make someone instantly understand what the product is about
                        {f'**CRITICAL - PROMOTION IN HEADLINE:**' if promotion_text else ''}
                        {f'- The promotion text "{promotion_text}" MUST be integrated into the headline itself' if promotion_text else ''}
                        {f'- **ABSOLUTELY CRITICAL: Preserve the promotion text EXACTLY as provided - do NOT abbreviate, truncate, or shorten ANY words**' if promotion_text else ''}
                        {f'- If the promotion text is "30% Winter Sale", you MUST display it as "30% WINTER SALE" (with ALL words complete), NOT "30% W SALE" or "30% W Sale" or any abbreviation' if promotion_text else ''}
                        {f'- NEVER abbreviate "Winter" to "W" or "Sale" to "S" - always use fully spelled-out words' if promotion_text else ''}
                        {f'- **DO NOT use pipe symbol "|" as a separator** - it looks unprofessional' if promotion_text else ''}
                        {f'- Instead, blend the promotion smoothly using: a dash "-", a comma ",", or integrate it naturally without separators' if promotion_text else ''}
                        {f'- Examples of GOOD integration: "ILLUMINATE WITH GRACE - 30% WINTER SALE" or "ELEVATE YOUR SPACE, 30% WINTER SALE" or "PREMIUM QUALITY 30% WINTER SALE"' if promotion_text else ''}
                        {f'- Examples of BAD integration: "ELEVATE YOUR SPACE | 30% W SALE" (pipe + abbreviation - DO NOT DO THIS)' if promotion_text else ''}
                        {f'- The promotion should flow naturally with the headline text and must be fully spelled out with ALL words intact' if promotion_text else ''}
                        {f'- Do NOT put the promotion in a separate element - it must be in the headline text field' if promotion_text else ''}

**TAGLINE MUST SPEAK TO THE TARGET AUDIENCE:**
- Who is the target audience? Think about their desires, pain points, aspirations
- Create a tagline that makes them think "this is exactly what I need"
- Reference their lifestyle, values, or the transformation the product offers
- DO NOT use vague phrases like "Crafted Perfection" or "Quality You Deserve"
- Be SPECIFIC about the benefit or emotion

**OTHER REQUIREMENTS:**
- Use EXACTLY the fonts specified above
- Features: Generate 3-5 product-specific features based on the actual product
- CTA: Create compelling call-to-action text. **CRITICAL: Position the CTA button BELOW the product with sufficient spacing (at least 60-80px gap). The button must NOT overlap with the product. Ensure clear separation between product and button.**
- Ensure ALL text has correct spelling and grammar
- Place text elements strategically based on the layout direction
{promotion_info and f"- Promotion: The promotion text '{promotion_text}' is already integrated into the headline - do NOT duplicate it elsewhere" or ""}
{f"**CRITICAL - PRICING EXCLUSION:** The user has chosen NOT to include pricing. DO NOT include any price tags, pricing badges, discount displays, or pricing information anywhere in the image. Completely exclude all pricing elements." if not include_price else ""}

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
            
            # Handle response.content which can be a string or list depending on langchain version
            raw_content = response.content
            if isinstance(raw_content, list):
                # Extract text from list of content parts
                prompt_text = " ".join(
                    part.get("text", str(part)) if isinstance(part, dict) else str(part)
                    for part in raw_content
                )
            else:
                prompt_text = str(raw_content) if raw_content else ""

            # Post-process to enforce full promotion text (prevent abbreviation like "W SALE")
            if promotion_text:
                prompt_text = self._enforce_full_promotion_text(prompt_text, promotion_text)
            
            # Extract structured information
            structured_prompt = self._parse_prompt(prompt_text)
            
            return {
                "success": True,
                "prompt": prompt_text,
                "structured_prompt": structured_prompt,
                "metadata": {
                    "image_path": image_path,
                    "product_persona": product_persona,
                    "description": description,
                    "user_inputs": user_inputs,
                    "font_styles": font_styles,
                    "include_price": include_price,
                    "logo_path": logo_path,
                    "promotion_text": promotion_text
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
                    "product_persona": product_persona,
                    "description": description,
                    "user_inputs": user_inputs
                }
            }
    
    def _enforce_full_promotion_text(self, prompt_text: str, promotion_text: str) -> str:
        """
        Ensure the promotion text is used verbatim (no abbreviations like "W SALE").
        If any partial/abbreviated form is detected, replace it with the full promotion text.
        """
        try:
            full_text = promotion_text.strip()
            if not full_text:
                return prompt_text

            # Normalize to uppercase for matching
            full_upper = full_text.upper()

            # Common bad patterns: "W SALE", "W SALE.", "W SALE\"", "W SALE'", etc.
            bad_patterns = [
                r'\bW\s+SALE\b',
                r'\bW\s+SALE\b[\.!",\']?'
            ]

            cleaned = prompt_text

            # Direct substitution of bad patterns with full text
            for pat in bad_patterns:
                cleaned = re.sub(pat, full_upper, cleaned, flags=re.IGNORECASE)

            # If truncated after the percent (e.g., "30% W SALE"), replace the whole clause with full text
            cleaned = re.sub(r'\b\d+%\s+W\s+SALE\b', full_upper, cleaned, flags=re.IGNORECASE)

            # Replace any occurrence of the promotion text but abbreviated (heuristic): "% W " or "%W "
            cleaned = re.sub(r'\b(\d+%)\s*W\s*SALE\b', lambda m: f"{m.group(1)} {full_upper.split(' ', 1)[-1] if ' ' in full_upper else full_upper}", cleaned, flags=re.IGNORECASE)

            # Final pass: if promotion text exists in lowercase/partial, enforce full uppercase verbatim
            cleaned = cleaned.replace(full_text, full_upper)

            return cleaned
        except Exception:
            return prompt_text
    
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
