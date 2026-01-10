"""
Product Analyser Agent
Analyzes product images using AI and collects comprehensive product information
Creates structured product persona for downstream agents
"""

import base64
import json
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv

load_dotenv()

class ProductAnalyserAgent:
    """
    Agent 1: Professional Product Analyser
    Analyzes product images using Gemini Vision API and collects user inputs
    Creates structured product persona dictionary
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the product analyser agent"""
        # Use specific key for product analysis, fall back to general key
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY_ANALYSER") or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY_ANALYSER or GOOGLE_API_KEY environment variable.")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-image-preview",
            google_api_key=self.api_key,
            temperature=0.7,
            max_tokens=2000
        )
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 for API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_product(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze product image using AI to understand product type, materials, features, etc.
        
        Args:
            image_path: Path to the product image
        
        Returns:
            Dictionary containing AI analysis results
        """
        try:
            # Build system prompt for product analysis
            system_prompt = """You are an expert product analyst and brand strategist specializing in e-commerce and advertising.
Your task is to analyze product images and extract comprehensive information for creating premium ad creatives.

Analyze the product image and provide a structured analysis including:

1. **Product Type/Category**: What type of product is this? (e.g., home decor, kitchenware, supplements, skincare, jewelry, electronics, etc.)
2. **Materials**: What materials are visible? (e.g., wood, metal, ceramic, fabric, glass, plastic, etc.)
3. **Key Features**: What are the visible features, design elements, or unique characteristics?
4. **Style/Aesthetic**: What is the design style? (e.g., modern, rustic, minimalist, luxury, premium, casual, sporty, etc.)
5. **Suggested Use Cases**: What are potential use cases or applications for this product?
6. **Target Market Indicators**: Based on the product's appearance, what market segment might this appeal to?

7. **BRAND POSITIONING** (CRITICAL - Choose ONE):
   - **LUXURY/PREMIUM**: High-end products like Hermès, Dior, Chanel, Bang & Olufsen, Apple. Characterized by: subtle colors, muted palettes, understated elegance, refined aesthetics, minimal text, exclusive feel.
   - **ASPIRATIONAL**: Mid-premium brands like Coach, Michael Kors, Samsung, Sony. Characterized by: polished look, sophisticated but accessible, quality materials.
   - **MASS CONSUMER**: Everyday products for general consumers. Products for daily use, practical, functional, value-oriented.
   - **SPORTY/ATHLETIC**: Nike, Adidas, Under Armour style. Bold, energetic, dynamic, bright colors, action-oriented.
   - **HEALTH/WELLNESS**: Supplements, vitamins, fitness products, health foods. Clean, trustworthy, benefit-focused.
   - **PLAYFUL/FUN**: Toys, games, candy, casual products. Bright, cheerful, energetic, fun colors.

8. **Key Selling Points**: List 3-5 unique benefits or features that should be highlighted in the ad.

Provide your analysis in a clear, structured format that can be used to create compelling ad copy.
Be specific and detailed - focus on what makes this product unique or appealing."""

            # Encode image
            base64_image = self.encode_image(image_path)
            
            # Prepare messages for Gemini
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=[
                    {
                        "type": "text",
                        "text": """Please analyze this product image in detail. Provide a comprehensive analysis covering:
- Product type/category
- Materials detected
- Key features and design elements
- Style and aesthetic
- Suggested use cases
- Target market indicators
- Brand Positioning (MUST be one of: LUXURY/PREMIUM, ASPIRATIONAL, MASS CONSUMER, SPORTY/ATHLETIC, HEALTH/WELLNESS, or PLAYFUL/FUN)
- Key Selling Points (3-5 benefits to highlight in ads)

Format your response as a structured analysis that can be used for advertising purposes."""
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
                analysis_text = " ".join(
                    part.get("text", str(part)) if isinstance(part, dict) else str(part)
                    for part in raw_content
                )
            else:
                analysis_text = str(raw_content) if raw_content else ""
            
            # Parse the analysis into structured format
            structured_analysis = self._parse_analysis(analysis_text)
            
            return {
                "success": True,
                "raw_analysis": analysis_text,
                "structured_analysis": structured_analysis,
                "metadata": {
                    "image_path": image_path,
                    "model_used": "gemini-2.5-flash-image-preview"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "raw_analysis": None,
                "structured_analysis": None,
                "metadata": {
                    "image_path": image_path
                }
            }
    
    def _parse_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """
        Parse the AI analysis text into structured format
        
        Args:
            analysis_text: Raw analysis text from AI
        
        Returns:
            Structured dictionary with parsed information
        """
        structured = {
            "product_type": "",
            "materials": [],
            "features": [],
            "style": "",
            "suggested_use_cases": [],
            "target_market_indicators": "",
            "brand_positioning": "MASS CONSUMER",  # Default positioning
            "key_selling_points": [],
            "font_styles": {},  # Will be populated by determine_font_styles()
            "ad_style": {}  # Will be populated by determine_ad_style()
        }
        
        # Try to extract structured information from the text
        lines = analysis_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            line_lower = line.lower()
            if "product type" in line_lower or "category" in line_lower:
                current_section = "product_type"
                # Extract value after colon
                if ':' in line:
                    structured["product_type"] = line.split(':', 1)[1].strip()
            elif "material" in line_lower:
                current_section = "materials"
                if ':' in line:
                    materials_str = line.split(':', 1)[1].strip()
                    # Split by comma or other delimiters
                    structured["materials"] = [m.strip() for m in materials_str.replace(',', '|').split('|') if m.strip()]
            elif "feature" in line_lower or "characteristic" in line_lower:
                current_section = "features"
                if ':' in line:
                    features_str = line.split(':', 1)[1].strip()
                    structured["features"] = [f.strip() for f in features_str.replace(',', '|').split('|') if f.strip()]
            elif "style" in line_lower or "aesthetic" in line_lower:
                current_section = "style"
                if ':' in line:
                    structured["style"] = line.split(':', 1)[1].strip()
            elif "use case" in line_lower or "application" in line_lower:
                current_section = "suggested_use_cases"
                if ':' in line:
                    use_cases_str = line.split(':', 1)[1].strip()
                    structured["suggested_use_cases"] = [uc.strip() for uc in use_cases_str.replace(',', '|').split('|') if uc.strip()]
            elif "target market" in line_lower or "market segment" in line_lower:
                current_section = "target_market_indicators"
                if ':' in line:
                    structured["target_market_indicators"] = line.split(':', 1)[1].strip()
            elif "brand positioning" in line_lower or "positioning" in line_lower:
                current_section = "brand_positioning"
                if ':' in line:
                    pos_text = line.split(':', 1)[1].strip().upper()
                    # Map to standard positioning categories
                    if any(kw in pos_text for kw in ["LUXURY", "PREMIUM", "HIGH-END", "HIGH END"]):
                        structured["brand_positioning"] = "LUXURY"
                    elif any(kw in pos_text for kw in ["ASPIRATIONAL", "MID-PREMIUM"]):
                        structured["brand_positioning"] = "ASPIRATIONAL"
                    elif any(kw in pos_text for kw in ["SPORTY", "ATHLETIC", "SPORT", "FITNESS"]):
                        structured["brand_positioning"] = "SPORTY"
                    elif any(kw in pos_text for kw in ["HEALTH", "WELLNESS", "SUPPLEMENT", "VITAMIN"]):
                        structured["brand_positioning"] = "HEALTH_WELLNESS"
                    elif any(kw in pos_text for kw in ["PLAYFUL", "FUN", "CASUAL", "CHEERFUL"]):
                        structured["brand_positioning"] = "PLAYFUL"
                    else:
                        structured["brand_positioning"] = "MASS CONSUMER"
            elif "selling point" in line_lower or "key benefit" in line_lower:
                current_section = "key_selling_points"
                if ':' in line:
                    points_str = line.split(':', 1)[1].strip()
                    if points_str:
                        structured["key_selling_points"] = [p.strip() for p in points_str.replace(',', '|').split('|') if p.strip()]
            elif current_section and line and not line.startswith('-') and not line.startswith('*'):
                # Continue adding to current section
                if current_section == "materials" and line:
                    structured["materials"].append(line.strip(' -•'))
                elif current_section == "features" and line:
                    structured["features"].append(line.strip(' -•'))
                elif current_section == "key_selling_points" and line:
                    structured["key_selling_points"].append(line.strip(' -•*'))
                elif current_section == "suggested_use_cases" and line:
                    structured["suggested_use_cases"].append(line.strip(' -•'))
        
        # Clean up empty strings
        structured["materials"] = [m for m in structured["materials"] if m]
        structured["features"] = [f for f in structured["features"] if f]
        structured["suggested_use_cases"] = [uc for uc in structured["suggested_use_cases"] if uc]
        structured["key_selling_points"] = [ksp for ksp in structured["key_selling_points"] if ksp]
        
        # Determine font styles based on product style
        structured["font_styles"] = self._determine_font_styles(structured["style"], structured["materials"])
        
        # Determine ad style based on brand positioning
        structured["ad_style"] = self._determine_ad_style(
            structured["brand_positioning"], 
            structured["style"],
            structured["key_selling_points"]
        )
        
        return structured
    
    def _determine_font_styles(self, style: str, materials: list) -> Dict[str, str]:
        """
        Determine appropriate font styles based on product style and materials.
        Returns descriptive font characteristics that AI image generators can understand.
        
        Args:
            style: Product style/aesthetic (e.g., "luxury", "modern", "rustic")
            materials: List of materials used in the product
        
        Returns:
            Dictionary with font style descriptions for each text element
        """
        style_lower = style.lower() if style else ""
        materials_lower = " ".join(materials).lower() if materials else ""
        
        # Default font styles
        font_styles = {
            "headline": "",
            "tagline": "",
            "cta": "",
            "price": ""
        }
        
        # Luxury/Premium/Elegant products
        if any(kw in style_lower for kw in ["luxury", "premium", "elegant", "sophisticated", "high-end", "upscale"]):
            font_styles["headline"] = "Elegant high-contrast serif typeface with refined thin-to-thick stroke variation, reminiscent of luxury fashion magazines like Vogue or Harper's Bazaar. Think Didot, Bodoni, or similar editorial elegance with commanding presence."
            font_styles["tagline"] = "Light-weight sophisticated sans-serif with generous letter-spacing and refined proportions. Subtle, understated elegance that complements without competing."
            font_styles["cta"] = "Clean, confident medium-weight sans-serif with balanced proportions. Professional and inviting without being aggressive."
            font_styles["price"] = "Clear, modern sans-serif with medium-bold weight. Highly legible with confident, trustworthy appearance."
        
        # Modern/Minimalist products
        elif any(kw in style_lower for kw in ["modern", "minimalist", "contemporary", "sleek", "clean"]):
            font_styles["headline"] = "Clean geometric sans-serif with even stroke widths and precise letterforms. Modern, confident, and uncluttered like Swiss design principles. Think Helvetica, Futura, or Avenir aesthetic."
            font_styles["tagline"] = "Light-weight geometric sans-serif with open letterforms and excellent readability. Minimal and refined."
            font_styles["cta"] = "Medium-weight geometric sans-serif with clear, confident letterforms. Simple and direct."
            font_styles["price"] = "Clean, modern sans-serif with medium weight. Precise and professional."
        
        # Rustic/Artisan/Handcrafted products
        elif any(kw in style_lower for kw in ["rustic", "artisan", "handcrafted", "handmade", "vintage", "traditional"]) or \
             any(kw in materials_lower for kw in ["wood", "leather", "ceramic", "clay", "natural"]):
            font_styles["headline"] = "Warm, organic serif typeface with subtle hand-crafted character and authentic feel. Traditional proportions with gentle curves, evoking craftsmanship and heritage. Think Garamond, Caslon, or artisanal book typography."
            font_styles["tagline"] = "Friendly, approachable sans-serif with warm personality and natural feel. Readable and welcoming."
            font_styles["cta"] = "Warm, rounded sans-serif with friendly character. Inviting and approachable."
            font_styles["price"] = "Clear, readable serif or sans-serif with warm, trustworthy character."
        
        # Bold/Contemporary/Edgy products
        elif any(kw in style_lower for kw in ["bold", "edgy", "urban", "industrial", "strong"]):
            font_styles["headline"] = "Bold, impactful sans-serif with strong presence and confident weight. Striking and memorable with powerful visual impact. Think Montserrat Bold, Oswald, or Impact-style typography."
            font_styles["tagline"] = "Medium-weight condensed sans-serif with strong, confident character. Direct and purposeful."
            font_styles["cta"] = "Bold, confident sans-serif with strong visual weight. Action-oriented and commanding."
            font_styles["price"] = "Bold, clear sans-serif with high contrast for immediate readability."
        
        # Playful/Fun/Casual products
        elif any(kw in style_lower for kw in ["playful", "fun", "casual", "friendly", "cheerful", "whimsical"]):
            font_styles["headline"] = "Rounded, friendly display typeface with warm, approachable character. Playful proportions with gentle curves that convey joy and accessibility."
            font_styles["tagline"] = "Friendly rounded sans-serif with open letterforms and casual warmth. Approachable and engaging."
            font_styles["cta"] = "Rounded, inviting sans-serif with friendly character. Welcoming and easy-going."
            font_styles["price"] = "Clean, friendly sans-serif with rounded terminals. Clear and approachable."
        
        # Classic/Traditional/Timeless products
        elif any(kw in style_lower for kw in ["classic", "timeless", "heritage", "refined"]):
            font_styles["headline"] = "Classic, well-proportioned serif typeface with balanced contrast and timeless elegance. Traditional letterforms with dignified presence, like Times, Baskerville, or Garamond."
            font_styles["tagline"] = "Refined, readable serif or light sans-serif with classical proportions. Understated and elegant."
            font_styles["cta"] = "Clean, balanced serif or sans-serif with classic proportions. Trustworthy and refined."
            font_styles["price"] = "Clear, traditional serif or sans-serif with excellent legibility."
        
        # Default fallback - Professional/Neutral
        else:
            font_styles["headline"] = "Professional, well-balanced serif or sans-serif typeface with clear hierarchy and confident presence. Versatile and appropriate for quality products."
            font_styles["tagline"] = "Clean, readable sans-serif with balanced proportions. Professional and approachable."
            font_styles["cta"] = "Clear, confident medium-weight sans-serif. Direct and professional."
            font_styles["price"] = "Clean, modern sans-serif with clear legibility."
        
        return font_styles
    
    def _determine_ad_style(self, brand_positioning: str, style: str, key_selling_points: list) -> Dict[str, Any]:
        """
        Determine the ad creative style based on brand positioning.
        Returns comprehensive style guidelines for diverse, professional ad creatives.
        
        Args:
            brand_positioning: The brand positioning category
            style: Product style/aesthetic
            key_selling_points: List of key selling points to highlight
        
        Returns:
            Dictionary with ad style specifications
        """
        import random
        
        # Define ad template styles based on reference images and professional standards
        ad_templates = {
            "LUXURY": {
                "templates": [
                    {
                        "name": "Editorial Elegance",
                        "description": "Minimalist luxury editorial style with generous white space",
                        "background": "Pure white or soft cream with subtle gradient, reminiscent of Vogue or Harper's Bazaar",
                        "color_palette": ["#FFFFFF", "#F5F5F0", "#1A1A1A", "#C9B037", "#2C2C2C"],
                        "layout": "Centered product with elegant serif headline above, minimal text, maximum negative space",
                        "mood": "Understated luxury, exclusive, refined"
                    },
                    {
                        "name": "Dark Luxury",
                        "description": "Moody, sophisticated dark background with dramatic lighting",
                        "background": "Deep charcoal or black with soft spotlight on product",
                        "color_palette": ["#1A1A1A", "#2D2D2D", "#C9B037", "#FFFFFF", "#8B7355"],
                        "layout": "Product hero with subtle golden accents, minimal elegant typography",
                        "mood": "Opulent, exclusive, mysterious"
                    },
                    {
                        "name": "Marble & Gold",
                        "description": "Luxurious marble texture with gold accents",
                        "background": "White marble with subtle gray veining, gold leaf accents",
                        "color_palette": ["#FFFFFF", "#E8E4E0", "#C9B037", "#1A1A1A", "#B8860B"],
                        "layout": "Asymmetric composition with product at golden ratio, refined serif typography",
                        "mood": "Timeless elegance, heritage luxury"
                    }
                ],
                "typography_rules": "Thin, elegant serifs with generous letter-spacing. Minimal text. Let the product speak.",
                "avoid": "Bright colors, busy layouts, discount badges, exclamation marks, casual language"
            },
            "ASPIRATIONAL": {
                "templates": [
                    {
                        "name": "Modern Sophistication",
                        "description": "Clean, contemporary aesthetic with subtle gradients",
                        "background": "Soft gradient from warm gray to cream",
                        "color_palette": ["#F8F6F4", "#E5DED5", "#2C3E50", "#C9956C", "#1A1A1A"],
                        "layout": "Product centered with clean typography, balanced composition",
                        "mood": "Polished, contemporary, accessible luxury"
                    },
                    {
                        "name": "Lifestyle Context",
                        "description": "Product in an aspirational lifestyle setting",
                        "background": "Warm, inviting interior setting or lifestyle scene",
                        "color_palette": ["#F5F0EB", "#D4C4B5", "#2C3E50", "#B8860B", "#1A1A1A"],
                        "layout": "Product in context with lifestyle elements, story-driven",
                        "mood": "Aspirational, attainable elegance"
                    }
                ],
                "typography_rules": "Modern serifs or refined sans-serifs. Clear hierarchy, professional.",
                "avoid": "Cheap-looking effects, overly casual language"
            },
            "SPORTY": {
                "templates": [
                    {
                        "name": "Dynamic Energy",
                        "description": "Bold, energetic design with dynamic angles",
                        "background": "Vibrant gradient with dynamic diagonal lines or geometric shapes",
                        "color_palette": ["#FF6B35", "#1A1A1A", "#FFFFFF", "#00D4FF", "#FFD700"],
                        "layout": "Dynamic diagonal composition, bold typography, action-oriented",
                        "mood": "Energetic, powerful, motivating"
                    },
                    {
                        "name": "Urban Athletic",
                        "description": "Street-style athletic aesthetic",
                        "background": "Concrete texture with bold color overlays",
                        "color_palette": ["#1A1A1A", "#FF0000", "#FFFFFF", "#00FF00", "#FFFF00"],
                        "layout": "Bold, in-your-face product placement, strong sans-serif typography",
                        "mood": "Urban, bold, confident"
                    },
                    {
                        "name": "Performance Focus",
                        "description": "Clean, technical aesthetic emphasizing performance",
                        "background": "Sleek gradient with subtle tech-inspired grid or lines",
                        "color_palette": ["#0A0A0A", "#00D4FF", "#FFFFFF", "#FF6B00", "#1A1A1A"],
                        "layout": "Product hero with technical callouts, performance metrics style",
                        "mood": "High-tech, professional athletic"
                    }
                ],
                "typography_rules": "Bold, condensed sans-serifs. Strong, impactful headlines. Action words.",
                "avoid": "Delicate serifs, muted colors, passive language"
            },
            "HEALTH_WELLNESS": {
                "templates": [
                    {
                        "name": "Clean Wellness",
                        "description": "Fresh, clean aesthetic with benefit-focused design like the PCOS Sidekick example",
                        "background": "Soft sky blue gradient or clean white with gentle color accents",
                        "color_palette": ["#87CEEB", "#FFFFFF", "#4A90A4", "#2D5A27", "#1A1A1A"],
                        "layout": "Product prominently displayed with 3-4 benefit icons/bullets on the side, clean headline at top",
                        "mood": "Trustworthy, clean, health-focused"
                    },
                    {
                        "name": "Natural Vitality",
                        "description": "Organic, nature-inspired wellness aesthetic",
                        "background": "Soft green gradient or natural texture with botanical elements",
                        "color_palette": ["#E8F5E9", "#4CAF50", "#2E7D32", "#FFFFFF", "#1A1A1A"],
                        "layout": "Product with natural elements, benefit-focused messaging",
                        "mood": "Natural, pure, healthy"
                    },
                    {
                        "name": "Split Comparison",
                        "description": "Before/after or comparison style like the Liver Function example",
                        "background": "Split screen with contrasting colors (healthy green/blue vs. warning red)",
                        "color_palette": ["#4CAF50", "#E53935", "#FFFFFF", "#1A1A1A", "#FFD700"],
                        "layout": "Dramatic split-screen comparison with bold messaging",
                        "mood": "Impactful, problem-solution oriented"
                    }
                ],
                "typography_rules": "Clean, readable sans-serifs. Trust-building, clear benefit statements.",
                "avoid": "Unsubstantiated claims, clinical coldness"
            },
            "PLAYFUL": {
                "templates": [
                    {
                        "name": "Bright & Cheerful",
                        "description": "Vibrant, fun design with playful elements",
                        "background": "Bright, cheerful gradient with fun shapes or patterns",
                        "color_palette": ["#FF69B4", "#00CED1", "#FFD700", "#FF6347", "#FFFFFF"],
                        "layout": "Playful, dynamic composition with fun typography",
                        "mood": "Joyful, fun, approachable"
                    },
                    {
                        "name": "Pop Art Inspired",
                        "description": "Bold, pop-art influenced design",
                        "background": "Bold color blocks with halftone patterns or comic-style elements",
                        "color_palette": ["#FF1493", "#00FF00", "#FFFF00", "#00BFFF", "#FFFFFF"],
                        "layout": "Bold, graphic composition with impactful typography",
                        "mood": "Bold, fun, eye-catching"
                    }
                ],
                "typography_rules": "Rounded, friendly fonts. Playful but readable. Fun language.",
                "avoid": "Serious, corporate aesthetics"
            },
            "MASS CONSUMER": {
                "templates": [
                    {
                        "name": "Lifestyle Elegant",
                        "description": "Warm, inviting lifestyle aesthetic like the Mixer example",
                        "background": "Warm beige or cream with soft, natural lighting",
                        "color_palette": ["#F5E6D3", "#E8D4B8", "#2C3E50", "#1A1A1A", "#FFFFFF"],
                        "layout": "Product in lifestyle context with elegant script headline, benefit icons below",
                        "mood": "Warm, inviting, relatable"
                    },
                    {
                        "name": "Clean Modern",
                        "description": "Clean, contemporary design with clear messaging",
                        "background": "Soft gradient or solid with subtle texture",
                        "color_palette": ["#F8F9FA", "#E9ECEF", "#495057", "#212529", "#007BFF"],
                        "layout": "Centered product with clear hierarchy, benefit statements",
                        "mood": "Modern, accessible, trustworthy"
                    },
                    {
                        "name": "Bold Value",
                        "description": "Strong promotional design with clear value proposition",
                        "background": "Bold color with dynamic elements",
                        "color_palette": ["#FF6B00", "#1A1A1A", "#FFFFFF", "#FFD700", "#00CED1"],
                        "layout": "Product hero with bold promotional messaging, clear CTA",
                        "mood": "Energetic, value-focused, action-oriented"
                    }
                ],
                "typography_rules": "Clear, readable fonts. Balanced between approachable and professional.",
                "avoid": "Overly cheap-looking designs, cluttered layouts"
            }
        }
        
        # Get the template set for this positioning
        positioning_key = brand_positioning if brand_positioning in ad_templates else "MASS CONSUMER"
        template_set = ad_templates[positioning_key]
        
        # Randomly select one template from the available options
        selected_template = random.choice(template_set["templates"])
        
        # Build the ad style dictionary
        ad_style = {
            "brand_positioning": brand_positioning,
            "template_name": selected_template["name"],
            "template_description": selected_template["description"],
            "background_style": selected_template["background"],
            "color_palette": selected_template["color_palette"],
            "layout_approach": selected_template["layout"],
            "mood": selected_template["mood"],
            "typography_rules": template_set["typography_rules"],
            "avoid": template_set["avoid"],
            "key_selling_points": key_selling_points[:4] if key_selling_points else [],  # Max 4 selling points
            "all_available_templates": [t["name"] for t in template_set["templates"]]
        }
        
        return ad_style
    
    def create_product_persona(self, image_analysis: Dict[str, Any], user_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combine AI analysis and user inputs into structured product persona
        
        Args:
            image_analysis: Result from analyze_product() method
            user_inputs: Dictionary containing user-provided information:
                - product_name: str
                - usp: str (product USP/use case)
                - target_audience: str
                - promotion: dict with keys: included (bool), percentage (int), before_price (str), after_price (str)
                - additional_comments: str
        
        Returns:
            Structured product persona dictionary
        """
        # Get structured analysis with defaults
        structured = image_analysis.get("structured_analysis", {})
        
        # Default ad style if not present
        default_ad_style = {
            "brand_positioning": "MASS CONSUMER",
            "template_name": "Clean Modern",
            "template_description": "Clean, contemporary design with clear messaging",
            "background_style": "Soft gradient or solid with subtle texture",
            "color_palette": ["#F8F9FA", "#E9ECEF", "#495057", "#212529", "#007BFF"],
            "layout_approach": "Centered product with clear hierarchy, benefit statements",
            "mood": "Modern, accessible, trustworthy",
            "typography_rules": "Clear, readable fonts. Balanced between approachable and professional.",
            "avoid": "Overly cheap-looking designs, cluttered layouts",
            "key_selling_points": []
        }
        
        persona = {
            "ai_analysis": {
                "product_type": structured.get("product_type", ""),
                "materials": structured.get("materials", []),
                "features": structured.get("features", []),
                "style": structured.get("style", ""),
                "suggested_use_cases": structured.get("suggested_use_cases", []),
                "target_market_indicators": structured.get("target_market_indicators", ""),
                "brand_positioning": structured.get("brand_positioning", "MASS CONSUMER"),
                "key_selling_points": structured.get("key_selling_points", []),
                "raw_analysis": image_analysis.get("raw_analysis", ""),
                "font_styles": structured.get("font_styles", {
                    "headline": "Professional serif or sans-serif with clear hierarchy",
                    "tagline": "Clean, readable sans-serif",
                    "cta": "Medium-weight sans-serif",
                    "price": "Clear, modern sans-serif"
                }),
                "ad_style": structured.get("ad_style", default_ad_style)
            },
            "user_inputs": {
                "product_name": user_inputs.get("product_name", ""),
                "usp": user_inputs.get("usp", ""),
                "target_audience": user_inputs.get("target_audience", ""),
                "promotion": {
                    "included": user_inputs.get("promotion", {}).get("included", False),
                    "percentage": user_inputs.get("promotion", {}).get("percentage", 0),
                    "before_price": user_inputs.get("promotion", {}).get("before_price", ""),
                    "after_price": user_inputs.get("promotion", {}).get("after_price", "")
                },
                "additional_comments": user_inputs.get("additional_comments", "")
            }
        }
        
        return persona


