"""
Test script for Complete Meta Ad Creative Workflow
Tests all 4 agents chained together
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from master_orchestrator import MasterOrchestrator

load_dotenv()

def test_complete_workflow():
    """Test the complete 4-agent workflow"""
    print("🎯 Complete Meta Ad Creative Workflow Test")
    print("="*70)
    print("🧠 Chains all 4 agents: Background Removal → Cropping → Prompt → Ad Creation")
    print("="*70)
    
    try:
        # Initialize master orchestrator
        orchestrator = MasterOrchestrator()
        
        # Get user inputs
        print("\n📋 Please provide the following information:")
        image_path = input("🖼️ Product image path: ").strip()
        
        if not os.path.exists(image_path):
            print(f"❌ Image not found: {image_path}")
            return
        
        # Optional: Get additional inputs upfront
        print("\n🔧 Optional inputs (press Enter to skip and provide later):")
        product_description = input("📄 Product description: ").strip() or None
        target_audience = input("👥 Target audience: ").strip() or None
        price = input("💰 Price (e.g., 'before 2999 Rs after 1899 Rs'): ").strip() or None
        
        print(f"\n✅ Starting workflow with:")
        print(f"   🖼️ Image: {image_path}")
        if product_description:
            print(f"   📄 Description: {product_description}")
        if target_audience:
            print(f"   👥 Audience: {target_audience}")
        if price:
            print(f"   💰 Price: {price}")
        
        # Run the complete workflow
        result = orchestrator.run_complete_workflow(
            image_path=image_path,
            product_description=product_description,
            target_audience=target_audience,
            price=price
        )
        
        if result["success"]:
            print("\n🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
            print("="*70)
            
            # Show all generated files
            outputs = result["final_outputs"]
            print("📁 Generated Files:")
            for step, file_path in outputs.items():
                if os.path.exists(file_path):
                    print(f"   ✅ {step}: {file_path}")
                else:
                    print(f"   ⚠️ {step}: {file_path} (file may not exist yet)")
            
            # Show workflow summary
            print(f"\n📊 Workflow Summary:")
            print(f"   Steps completed: {len(result['workflow_results']['steps_completed'])}")
            print(f"   Final Meta ad: {outputs.get('final_meta_ad', 'Not generated')}")
            
        else:
            print(f"\n❌ WORKFLOW FAILED!")
            print(f"   Error: {result['error']}")
            print(f"   Failed at step: {result.get('workflow_step', 'Unknown')}")
            
            if 'workflow_results' in result:
                completed_steps = result['workflow_results'].get('steps_completed', [])
                if completed_steps:
                    print(f"   Completed steps: {', '.join(completed_steps)}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_complete_workflow()
