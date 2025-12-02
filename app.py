"""
Streamlit Application for Meta Ad Creative Generator
Minimal design with orange and black color palette
"""

import streamlit as st
import os
import json
import time
from PIL import Image
from dotenv import load_dotenv

# Import agents
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from background_remover_agent import BackgroundRemoverAgent
from image_cropper_agent import ImageCropperAgent
from agent1_prompt_generator import PromptGeneratorAgent
from agent2_creative_generator import CreativeGeneratorAgent

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Meta Ad Creative Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for orange and black theme
st.markdown("""
    <style>
    .main {
        background-color: #000000;
    }
    .stButton>button {
        background-color: #FF6600;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #FF8533;
        color: white;
    }
    h1, h2, h3 {
        color: #FF6600;
    }
    .stTextInput>div>div>input {
        background-color: #1a1a1a;
        color: white;
    }
    .stTextArea>div>div>textarea {
        background-color: #1a1a1a;
        color: white;
    }
    .stSelectbox>div>div>select {
        background-color: #1a1a1a;
        color: white;
    }
    .sidebar .sidebar-content {
        background-color: #0a0a0a;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None
if 'image_path' not in st.session_state:
    st.session_state.image_path = None
if 'white_bg_path' not in st.session_state:
    st.session_state.white_bg_path = None
if 'cropped_path' not in st.session_state:
    st.session_state.cropped_path = None
if 'prompt' not in st.session_state:
    st.session_state.prompt = None
if 'final_creative_path' not in st.session_state:
    st.session_state.final_creative_path = None
if 'workflow_step' not in st.session_state:
    st.session_state.workflow_step = 'upload'  # upload, processing, prompt_input, prompt_review, generating, complete

def reset_workflow():
    """Reset the workflow to start over"""
    st.session_state.workflow_step = 'upload'
    st.session_state.white_bg_path = None
    st.session_state.cropped_path = None
    st.session_state.prompt = None
    st.session_state.final_creative_path = None

def save_uploaded_file(uploaded_file):
    """Save uploaded file to temporary directory"""
    # Create temp_uploads directory if it doesn't exist
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Generate unique filename
    timestamp = int(time.time())
    file_extension = os.path.splitext(uploaded_file.name)[1]
    filename = f"upload_{timestamp}{file_extension}"
    file_path = os.path.join(temp_dir, filename)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# Sidebar - How to Use
with st.sidebar:
    st.title("📖 How to Use")
    st.markdown("""
    ### Step 1: Upload Image
    Upload your product image using the file uploader on the main page.
    
    ### Step 2: Preview & Process
    Review your uploaded image, then click **"Create Generative"** to start processing.
    
    ### Step 3: Background Removal & Cropping
    The system will automatically:
    - Remove the background
    - Crop to 1:1 ratio
    - Center the product
    
    ### Step 4: Review Cropped Image
    Review the processed image and confirm to proceed with prompt generation.
    
    ### Step 5: Enter Product Details
    Provide:
    - Product description
    - Target audience
    - Price information
    
    ### Step 6: Review & Edit Prompt
    Review the generated prompt. You can edit:
    - Headline
    - Footer
    - Limited time offer
    
    ### Step 7: Generate Creative
    Confirm the prompt to generate your final Meta ad creative!
    """)
    
    st.markdown("---")
    if st.button("🔄 Reset Workflow", width='stretch'):
        reset_workflow()
        st.rerun()

# Main content
st.title("🎨 Meta Ad Creative Generator")
st.markdown("Transform your product images into premium Meta ad creatives using AI")

# Workflow Step 1: Image Upload
if st.session_state.workflow_step == 'upload':
    st.header("📸 Step 1: Upload Product Image")
    
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['png', 'jpg', 'jpeg', 'webp'],
        help="Upload your product image"
    )
    
    if uploaded_file is not None:
        # Save uploaded file
        image_path = save_uploaded_file(uploaded_file)
        st.session_state.image_path = image_path
        
        # Display image preview
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", width='stretch')
        st.session_state.uploaded_image = image
        
        # Create Generative button
        if st.button("🚀 Create Generative", width='stretch', type="primary"):
            st.session_state.workflow_step = 'processing'
            st.rerun()

# Workflow Step 2: Processing (Background Removal + Cropping)
elif st.session_state.workflow_step == 'processing':
    st.header("⚙️ Processing Image")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Initialize agents
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            st.error("❌ Google API key not found. Please set GOOGLE_API_KEY in your .env file.")
            st.stop()
        
        background_remover = BackgroundRemoverAgent(api_key)
        image_cropper = ImageCropperAgent()
        
        # Step 1: Background Removal
        status_text.text("🧹 Step 1/2: Removing background...")
        progress_bar.progress(25)
        
        bg_result = background_remover.remove_background(st.session_state.image_path)
        
        if not bg_result["success"]:
            st.error(f"❌ Background removal failed: {bg_result.get('error', 'Unknown error')}")
            if st.button("🔙 Go Back"):
                reset_workflow()
                st.rerun()
            st.stop()
        
        st.session_state.white_bg_path = bg_result["output_path"]
        progress_bar.progress(50)
        
        # Step 2: Cropping
        status_text.text("✂️ Step 2/2: Cropping to 1:1 ratio...")
        progress_bar.progress(75)
        
        crop_result = image_cropper.crop_to_square(st.session_state.white_bg_path)
        
        if not crop_result["success"]:
            st.error(f"❌ Cropping failed: {crop_result.get('error', 'Unknown error')}")
            if st.button("🔙 Go Back"):
                reset_workflow()
                st.rerun()
            st.stop()
        
        st.session_state.cropped_path = crop_result["output_path"]
        progress_bar.progress(100)
        status_text.text("✅ Processing complete!")
        
        # Show result
        st.success("✅ Image processed successfully!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original Image")
            st.image(st.session_state.image_path, width='stretch')
        
        with col2:
            st.subheader("Processed Image (Cropped)")
            cropped_image = Image.open(st.session_state.cropped_path)
            st.image(cropped_image, width='stretch')
        
        st.markdown("---")
        
        # Confirm to proceed
        if st.button("✅ Confirm & Generate Prompt", width='stretch', type="primary"):
            st.session_state.workflow_step = 'prompt_input'
            st.rerun()
        
        if st.button("🔙 Start Over"):
            reset_workflow()
            st.rerun()
    
    except Exception as e:
        st.error(f"❌ Error during processing: {str(e)}")
        if st.button("🔙 Go Back"):
            reset_workflow()
            st.rerun()

# Workflow Step 3: Prompt Input
elif st.session_state.workflow_step == 'prompt_input':
    st.header("📝 Step 2: Product Details")
    
    # Show cropped image
    if st.session_state.cropped_path:
        st.subheader("Processed Image")
        st.image(st.session_state.cropped_path, width=400)
    
    st.markdown("---")
    
    # Product details form
    with st.form("product_details_form"):
        product_description = st.text_input(
            "📄 Product Description",
            placeholder="e.g., Premium wooden photo frame with mother-of-pearl inlay",
            help="Describe your product"
        )
        
        target_audience = st.text_input(
            "👥 Target Audience",
            placeholder="e.g., Home decor enthusiasts, luxury buyers",
            help="Who is this product for?"
        )
        
        price = st.text_input(
            "💰 Price Information",
            placeholder="e.g., before 2999 Rs after 1899 Rs",
            help="Original price and discounted price"
        )
        
        submitted = st.form_submit_button("🚀 Generate Prompt", width='stretch', type="primary")
        
        if submitted:
            if not product_description or not target_audience or not price:
                st.warning("⚠️ Please fill in all fields")
            else:
                st.session_state.workflow_step = 'generating_prompt'
                st.session_state.product_description = product_description
                st.session_state.target_audience = target_audience
                st.session_state.price = price
                st.rerun()
    
    if st.button("🔙 Go Back"):
        st.session_state.workflow_step = 'processing'
        st.rerun()

# Workflow Step 4: Generating Prompt
elif st.session_state.workflow_step == 'generating_prompt':
    st.header("🤖 Generating Prompt...")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.text("🎯 Analyzing product and generating structured prompt...")
    progress_bar.progress(50)
    
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        prompt_generator = PromptGeneratorAgent(api_key)
        
        user_inputs = {
            "target_audience": st.session_state.target_audience,
            "price": st.session_state.price
        }
        
        prompt_result = prompt_generator.generate_prompt(
            st.session_state.cropped_path,
            st.session_state.product_description,
            user_inputs
        )
        
        if not prompt_result["success"]:
            st.error(f"❌ Prompt generation failed: {prompt_result.get('error', 'Unknown error')}")
            if st.button("🔙 Go Back"):
                st.session_state.workflow_step = 'prompt_input'
                st.rerun()
            st.stop()
        
        # Clean the prompt (remove markdown if present)
        generated_prompt = prompt_result["prompt"]
        if generated_prompt.startswith('```json'):
            generated_prompt = generated_prompt[7:]
        if generated_prompt.endswith('```'):
            generated_prompt = generated_prompt[:-3]
        generated_prompt = generated_prompt.strip()
        
        st.session_state.prompt = generated_prompt
        progress_bar.progress(100)
        status_text.text("✅ Prompt generated!")
        
        st.session_state.workflow_step = 'prompt_review'
        st.rerun()
    
    except Exception as e:
        st.error(f"❌ Error generating prompt: {str(e)}")
        if st.button("🔙 Go Back"):
            st.session_state.workflow_step = 'prompt_input'
            st.rerun()

# Workflow Step 5: Prompt Review & Edit
elif st.session_state.workflow_step == 'prompt_review':
    st.header("📋 Step 3: Review & Edit Prompt")
    
    if st.session_state.prompt:
        # Try to parse JSON for editing
        try:
            prompt_json = json.loads(st.session_state.prompt)
            
            # Extract editable fields
            headline = prompt_json.get("typography_and_layout", {}).get("headline", {}).get("text", "")
            footer = prompt_json.get("typography_and_layout", {}).get("footer", {}).get("text", "")
            limited_offer = prompt_json.get("typography_and_layout", {}).get("limited_time_offer", {}).get("text", "")
            
            st.subheader("✏️ Edit Text Elements")
            
            # Editable fields
            edited_headline = st.text_input("📰 Headline", value=headline)
            edited_footer = st.text_input("📄 Footer", value=footer)
            edited_offer = st.text_input("⏰ Limited Time Offer", value=limited_offer)
            
            # Update JSON if edited
            if edited_headline != headline or edited_footer != footer or edited_offer != limited_offer:
                prompt_json["typography_and_layout"]["headline"]["text"] = edited_headline
                prompt_json["typography_and_layout"]["footer"]["text"] = edited_footer
                prompt_json["typography_and_layout"]["limited_time_offer"]["text"] = edited_offer
                st.session_state.prompt = json.dumps(prompt_json, indent=2)
            
            st.markdown("---")
            st.subheader("📄 Full Prompt (JSON)")
            
            # Show full prompt in expandable section
            with st.expander("View Full Prompt JSON"):
                st.code(st.session_state.prompt, language="json")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✅ Confirm & Generate Creative", width='stretch', type="primary"):
                    st.session_state.workflow_step = 'generating_creative'
                    st.rerun()
            
            with col2:
                if st.button("🔙 Go Back", width='stretch'):
                    st.session_state.workflow_step = 'prompt_input'
                    st.rerun()
        
        except json.JSONDecodeError:
            st.warning("⚠️ Could not parse prompt as JSON. Showing raw prompt.")
            st.text_area("Generated Prompt", st.session_state.prompt, height=300)
            
            if st.button("✅ Confirm & Generate Creative", width='stretch', type="primary"):
                st.session_state.workflow_step = 'generating_creative'
                st.rerun()
            
            if st.button("🔙 Go Back", width='stretch'):
                st.session_state.workflow_step = 'prompt_input'
                st.rerun()

# Workflow Step 6: Generating Creative
elif st.session_state.workflow_step == 'generating_creative':
    st.header("🎨 Generating Final Creative...")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.text("🎯 Generating Meta ad creative with Nano Banana...")
    progress_bar.progress(50)
    
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        creative_generator = CreativeGeneratorAgent(api_key)
        
        creative_result = creative_generator.generate_creative(
            st.session_state.cropped_path,
            st.session_state.prompt,
            st.session_state.product_description
        )
        
        if not creative_result["success"]:
            st.error(f"❌ Creative generation failed: {creative_result.get('error', 'Unknown error')}")
            if st.button("🔙 Go Back"):
                st.session_state.workflow_step = 'prompt_review'
                st.rerun()
            st.stop()
        
        st.session_state.final_creative_path = creative_result["output_path"]
        progress_bar.progress(100)
        status_text.text("✅ Creative generated!")
        
        st.session_state.workflow_step = 'complete'
        st.rerun()
    
    except Exception as e:
        st.error(f"❌ Error generating creative: {str(e)}")
        if st.button("🔙 Go Back"):
            st.session_state.workflow_step = 'prompt_review'
            st.rerun()

# Workflow Step 7: Complete
elif st.session_state.workflow_step == 'complete':
    st.header("🎉 Your Meta Ad Creative is Ready!")
    
    if st.session_state.final_creative_path and os.path.exists(st.session_state.final_creative_path):
        # Display final creative - centered
        st.markdown("<br>", unsafe_allow_html=True)
        final_image = Image.open(st.session_state.final_creative_path)
        
        # Center the image
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(final_image, caption="Final Meta Ad Creative", width='stretch')
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Download button - prominent
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with open(st.session_state.final_creative_path, "rb") as file:
                st.download_button(
                    label="📥 Download Final Creative",
                    data=file,
                    file_name=os.path.basename(st.session_state.final_creative_path),
                    mime="image/jpeg",
                    width='stretch',
                    type="primary"
                )
        
        st.markdown("---")
        
        # Start new workflow
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Create Another Creative", width='stretch', type="primary"):
                reset_workflow()
                st.rerun()
    else:
        st.error("❌ Final creative not found. Please try again.")
        if st.button("🔙 Start Over"):
            reset_workflow()
            st.rerun()

