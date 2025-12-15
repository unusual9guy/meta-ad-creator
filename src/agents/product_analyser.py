"""
Product Analyser Agent
Analyzes product images using AI and collects comprehensive product information
Creates structured product persona for downstream agents
"""

import base64
import json
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
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
            system_prompt = """You are an expert product analyst specializing in e-commerce and advertising.
Your task is to analyze product images and extract comprehensive information about the product.

Analyze the product image and provide a structured analysis including:

1. **Product Type/Category**: What type of product is this? (e.g., home decor, kitchenware, photo frame, organizer, etc.)
2. **Materials**: What materials are visible? (e.g., wood, metal, ceramic, fabric, etc.)
3. **Key Features**: What are the visible features, design elements, or unique characteristics?
4. **Style/Aesthetic**: What is the design style? (e.g., modern, rustic, minimalist, luxury, etc.)
5. **Suggested Use Cases**: What are potential use cases or applications for this product?
6. **Target Market Indicators**: Based on the product's appearance, what market segment might this appeal to?

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
            analysis_text = response.content
            
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
            "target_market_indicators": ""
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
            elif current_section and line and not line.startswith('-') and not line.startswith('*'):
                # Continue adding to current section
                if current_section == "materials" and line:
                    structured["materials"].append(line.strip(' -•'))
                elif current_section == "features" and line:
                    structured["features"].append(line.strip(' -•'))
                elif current_section == "suggested_use_cases" and line:
                    structured["suggested_use_cases"].append(line.strip(' -•'))
        
        # Clean up empty strings
        structured["materials"] = [m for m in structured["materials"] if m]
        structured["features"] = [f for f in structured["features"] if f]
        structured["suggested_use_cases"] = [uc for uc in structured["suggested_use_cases"] if uc]
        
        return structured
    
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
        persona = {
            "ai_analysis": {
                "product_type": image_analysis.get("structured_analysis", {}).get("product_type", ""),
                "materials": image_analysis.get("structured_analysis", {}).get("materials", []),
                "features": image_analysis.get("structured_analysis", {}).get("features", []),
                "style": image_analysis.get("structured_analysis", {}).get("style", ""),
                "suggested_use_cases": image_analysis.get("structured_analysis", {}).get("suggested_use_cases", []),
                "target_market_indicators": image_analysis.get("structured_analysis", {}).get("target_market_indicators", ""),
                "raw_analysis": image_analysis.get("raw_analysis", "")
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

