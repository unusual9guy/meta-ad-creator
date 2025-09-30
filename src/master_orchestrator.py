"""
Master Orchestrator
Chains all 4 agents together for complete Meta ad creative generation
Flow: Background Removal → Cropping → Prompt Generation → Ad Creation
"""

import os
import sys
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Import all agents
from background_remover_agent import BackgroundRemoverAgent
from image_cropper_agent import ImageCropperAgent
from agent1_prompt_generator import PromptGeneratorAgent
from agent2_creative_generator import CreativeGeneratorAgent

load_dotenv()

class MasterOrchestrator:
    """
    Master orchestrator that chains all 4 agents for complete Meta ad creative generation
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the master orchestrator with all agents"""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
        
        # Initialize all agents
        print("🚀 Initializing all agents...")
        self.background_remover = BackgroundRemoverAgent(self.api_key)
        self.image_cropper = ImageCropperAgent()
        self.prompt_generator = PromptGeneratorAgent(self.api_key)
        self.creative_generator = CreativeGeneratorAgent(self.api_key)
        print("✅ All agents initialized successfully!")
    
    def run_complete_workflow(self, image_path: str, product_description: str = None, 
                            target_audience: str = None, price: str = None) -> Dict[str, Any]:
        """
        Run the complete 4-agent workflow
        
        Args:
            image_path: Path to the original product image
            product_description: Product description (will ask if not provided)
            target_audience: Target audience (will ask if not provided)
            price: Price information (will ask if not provided)
        
        Returns:
            Dictionary containing results from all agents
        """
        try:
            print("🎯 Starting Complete Meta Ad Creative Workflow")
            print("="*70)
            
            # Validate input image
            if not os.path.exists(image_path):
                return {
                    "success": False,
                    "error": f"Image not found: {image_path}",
                    "workflow_step": "validation"
                }
            
            workflow_results = {
                "original_image": image_path,
                "steps_completed": [],
                "final_outputs": {},
                "success": False
            }
            
            # STEP 1: Background Removal
            print("\n🧹 STEP 1: Background Removal")
            print("-" * 50)
            print("🎯 Removing background and replacing with white...")
            
            bg_result = self.background_remover.remove_background(image_path)
            
            if not bg_result["success"]:
                return {
                    "success": False,
                    "error": f"Background removal failed: {bg_result['error']}",
                    "workflow_step": "background_removal",
                    "workflow_results": workflow_results
                }
            
            white_bg_path = bg_result["output_path"]
            workflow_results["steps_completed"].append("background_removal")
            workflow_results["final_outputs"]["white_background_image"] = white_bg_path
            print(f"✅ Background removed! Saved to: {white_bg_path}")
            
            # STEP 2: Intelligent Cropping
            print("\n✂️ STEP 2: Intelligent Cropping")
            print("-" * 50)
            print("🎯 Cropping to 1:1 ratio with auto-centering...")
            
            crop_result = self.image_cropper.crop_to_square(white_bg_path)
            
            if not crop_result["success"]:
                return {
                    "success": False,
                    "error": f"Cropping failed: {crop_result['error']}",
                    "workflow_step": "cropping",
                    "workflow_results": workflow_results
                }
            
            cropped_path = crop_result["output_path"]
            workflow_results["steps_completed"].append("cropping")
            workflow_results["final_outputs"]["cropped_image"] = cropped_path
            print(f"✅ Image cropped! Saved to: {cropped_path}")
            
            # STEP 3: Get User Inputs (if not provided)
            print("\n📝 STEP 3: Prompt Generation Setup")
            print("-" * 50)
            
            if not product_description:
                product_description = input("📄 Enter product description: ").strip()
            
            if not target_audience:
                target_audience = input("👥 Enter target audience: ").strip()
            
            if not price:
                price = input("💰 Enter price (e.g., 'before 2999 Rs after 1899 Rs'): ").strip()
            
            user_inputs = {
                "target_audience": target_audience,
                "price": price
            }
            
            print(f"✅ User inputs received:")
            print(f"   📄 Description: {product_description}")
            print(f"   👥 Audience: {target_audience}")
            print(f"   💰 Price: {price}")
            
            # STEP 4: Prompt Generation
            print("\n📝 STEP 4: Prompt Generation")
            print("-" * 50)
            print("🎯 Generating structured prompt for Nano Banana...")
            
            prompt_result = self.prompt_generator.generate_prompt(
                cropped_path, 
                product_description, 
                user_inputs
            )
            
            if not prompt_result["success"]:
                return {
                    "success": False,
                    "error": f"Prompt generation failed: {prompt_result['error']}",
                    "workflow_step": "prompt_generation",
                    "workflow_results": workflow_results
                }
            
            generated_prompt = prompt_result["prompt"]
            workflow_results["steps_completed"].append("prompt_generation")
            workflow_results["final_outputs"]["generated_prompt"] = generated_prompt
            
            # Clean the prompt (remove markdown if present)
            if generated_prompt.startswith('```json'):
                generated_prompt = generated_prompt[7:]
            if generated_prompt.endswith('```'):
                generated_prompt = generated_prompt[:-3]
            generated_prompt = generated_prompt.strip()
            
            print("✅ Prompt generated successfully!")
            
            # Human Review of Generated Content
            print("\n🔍 STEP 5: Human Review")
            print("-" * 50)
            print("📋 Reviewing generated content...")
            
            try:
                import json
                prompt_json = json.loads(generated_prompt)
                headline = prompt_json.get("typography_and_layout", {}).get("headline", {}).get("text", "")
                footer = prompt_json.get("typography_and_layout", {}).get("footer", {}).get("text", "")
                limited_offer = prompt_json.get("typography_and_layout", {}).get("limited_time_offer", {}).get("text", "")
                
                if headline:
                    print(f"\n📰 Generated Headline: '{headline}'")
                if footer:
                    print(f"\n📄 Generated Footer: '{footer}'")
                if limited_offer:
                    print(f"\n⏰ Generated Limited Offer: '{limited_offer}'")
                
                print("\n🤔 Do you want to keep these generated texts?")
                print("   [y] Yes, proceed with these")
                print("   [n] No, let me provide custom ones")
                
                while True:
                    choice = input("\nEnter your choice (y/n): ").lower().strip()
                    if choice in ['y', 'yes']:
                        print("✅ Proceeding with generated content!")
                        break
                    elif choice in ['n', 'no']:
                        custom_headline = input("📰 Enter your custom headline: ").strip()
                        custom_footer = input("📄 Enter your custom footer: ").strip()
                        custom_offer = input("⏰ Enter your custom limited offer: ").strip()
                        
                        if custom_headline or custom_footer or custom_offer:
                            print("✅ Custom content received!")
                            if custom_headline:
                                prompt_json["typography_and_layout"]["headline"]["text"] = custom_headline
                            if custom_footer:
                                prompt_json["typography_and_layout"]["footer"]["text"] = custom_footer
                            if custom_offer:
                                prompt_json["typography_and_layout"]["limited_time_offer"]["text"] = custom_offer
                            
                            generated_prompt = json.dumps(prompt_json, indent=2)
                            print("📝 Updated prompt with custom content!")
                        break
                    else:
                        print("❌ Invalid choice. Please enter y or n.")
                        
            except json.JSONDecodeError:
                print("⚠️ Could not parse JSON prompt for review.")
                print("📝 Proceeding with raw prompt output...")
            
            # STEP 6: Ad Creative Generation
            print("\n🎨 STEP 6: Ad Creative Generation")
            print("-" * 50)
            print("🎯 Generating final Meta ad creative...")
            
            creative_result = self.creative_generator.generate_creative(
                cropped_path, 
                generated_prompt, 
                product_description
            )
            
            if not creative_result["success"]:
                return {
                    "success": False,
                    "error": f"Ad creative generation failed: {creative_result['error']}",
                    "workflow_step": "ad_creation",
                    "workflow_results": workflow_results
                }
            
            final_creative_path = creative_result["output_path"]
            workflow_results["steps_completed"].append("ad_creation")
            workflow_results["final_outputs"]["final_meta_ad"] = final_creative_path
            
            print("✅ Meta ad creative generated successfully!")
            print(f"💾 Final creative saved to: {final_creative_path}")
            
            # FINAL SUCCESS
            workflow_results["success"] = True
            print("\n" + "="*70)
            print("🎉 COMPLETE WORKFLOW SUCCESSFUL!")
            print("="*70)
            print("📁 Generated Files:")
            print(f"   🧹 White background: {white_bg_path}")
            print(f"   ✂️ Cropped image: {cropped_path}")
            print(f"   🎨 Final Meta ad: {final_creative_path}")
            
            return {
                "success": True,
                "message": "Complete workflow executed successfully!",
                "workflow_results": workflow_results,
                "final_outputs": workflow_results["final_outputs"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Workflow failed: {str(e)}",
                "workflow_step": "unknown",
                "workflow_results": workflow_results if 'workflow_results' in locals() else {}
            }
