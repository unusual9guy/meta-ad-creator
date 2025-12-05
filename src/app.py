"""
Streamlit Application for Meta Ad Creative Generator
Professional minimal design with orange and black color palette
"""

import streamlit as st
import os
import json
import time
from PIL import Image
from dotenv import load_dotenv

# Import agents
from agents.background_remover import BackgroundRemoverAgent
from agents.image_cropper import ImageCropperAgent
from agents.prompt_generator import PromptGeneratorAgent
from agents.creative_generator import CreativeGeneratorAgent

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Meta Ad Creative Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Comprehensive Professional CSS
st.markdown("""
    <style>
    /* Global Styles */
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    }
    
    /* Main Container */
    .main {
        background: linear-gradient(180deg, #000000 0%, #0a0a0a 100%);
        padding: 0;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Typography */
    h1 {
        color: #FF6600;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -0.03em;
        line-height: 1.1;
    }
    
    h2 {
        color: #FF6600;
        font-size: 2rem;
        font-weight: 700;
        margin-top: 2.5rem;
        margin-bottom: 1rem;
        letter-spacing: -0.02em;
    }
    
    h3 {
        color: #ffffff;
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    /* Subtitle */
    .subtitle {
        color: #888888;
        font-size: 1.1rem;
        margin-bottom: 3rem;
        line-height: 1.6;
    }
    
    /* Cards */
    .card {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Buttons - Primary */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #FF6600 0%, #FF8533 100%);
        color: #ffffff;
        border: none;
        border-radius: 10px;
        padding: 1rem 3rem;
        font-weight: 700;
        font-size: 1.1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 6px 20px rgba(255, 102, 0, 0.4);
        width: 100%;
        letter-spacing: 0.5px;
    }
    
    .stButton>button[kind="primary"]:hover {
        background: linear-gradient(135deg, #FF8533 0%, #FF6600 100%);
        box-shadow: 0 8px 30px rgba(255, 102, 0, 0.5);
        transform: translateY(-2px);
    }
    
    /* Buttons - Secondary */
    .stButton>button:not([kind="primary"]) {
        background-color: #1a1a1a;
        color: #ffffff;
        border: 2px solid #333333;
        border-radius: 10px;
        padding: 0.875rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton>button:not([kind="primary"]):hover {
        background-color: #252525;
        border-color: #FF6600;
        color: #FF6600;
        transform: translateY(-1px);
    }
    
    /* Form Inputs */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 2px solid #333333 !important;
        border-radius: 8px !important;
        padding: 0.875rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #FF6600 !important;
        box-shadow: 0 0 0 3px rgba(255, 102, 0, 0.15) !important;
        outline: none !important;
    }
    
    .stTextInput label,
    .stTextArea label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* File Uploader */
    .uploadedFile {
        border: 3px dashed #333333 !important;
        border-radius: 12px !important;
        padding: 2rem !important;
        background-color: #1a1a1a !important;
        transition: all 0.3s ease !important;
    }
    
    .uploadedFile:hover {
        border-color: #FF6600 !important;
        background-color: #1f1f1f !important;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #0a0a0a;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #0a0a0a 0%, #000000 100%);
        border-right: 1px solid #1a1a1a;
    }
    
    .sidebar h1,
    .sidebar h2,
    .sidebar h3 {
        color: #FF6600;
    }
    
    .sidebar p,
    .sidebar li {
        color: #aaaaaa;
        line-height: 1.8;
        font-size: 0.95rem;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #FF6600 0%, #FF8533 100%);
        border-radius: 10px;
    }
    
    /* Success/Error/Warning Messages */
    .stSuccess {
        background-color: rgba(255, 102, 0, 0.15) !important;
        border-left: 4px solid #FF6600 !important;
        padding: 1.25rem !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }
    
    .stError {
        background-color: rgba(220, 38, 38, 0.15) !important;
        border-left: 4px solid #dc2626 !important;
        padding: 1.25rem !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }
    
    .stWarning {
        background-color: rgba(255, 193, 7, 0.15) !important;
        border-left: 4px solid #ffc107 !important;
        padding: 1.25rem !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }
    
    /* Code Blocks */
    .stCodeBlock {
        background-color: #1a1a1a !important;
        border: 1px solid #333333 !important;
        border-radius: 8px !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    /* Divider */
    hr {
        border: none;
        border-top: 1px solid #2a2a2a;
        margin: 3rem 0;
    }
    
    /* Images */
    [data-testid="stImage"] {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
        border: 1px solid #2a2a2a;
    }
    
    /* Text */
    p, .stMarkdown {
        color: #cccccc;
        line-height: 1.8;
        font-size: 1rem;
    }
    
    /* Form Container */
    .stForm {
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 16px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Status Text */
    .status-text {
        color: #FF6600;
        font-weight: 600;
        font-size: 1.1rem;
        margin: 1rem 0;
    }
    
    /* Section Spacing */
    .section-spacer {
        height: 3rem;
    }
    
    /* Centered Content */
    .centered {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
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
    st.session_state.workflow_step = 'upload'
if 'logo_path' not in st.session_state:
    st.session_state.logo_path = None
if 'primary_font' not in st.session_state:
    st.session_state.primary_font = None
if 'secondary_font' not in st.session_state:
    st.session_state.secondary_font = None
if 'pricing_font' not in st.session_state:
    st.session_state.pricing_font = None
if 'include_price' not in st.session_state:
    st.session_state.include_price = True

def reset_workflow():
    """Reset the workflow to start over"""
    st.session_state.workflow_step = 'upload'
    st.session_state.white_bg_path = None
    st.session_state.cropped_path = None
    st.session_state.prompt = None
    st.session_state.final_creative_path = None
    st.session_state.logo_path = None
    st.session_state.primary_font = None
    st.session_state.secondary_font = None
    st.session_state.pricing_font = None
    st.session_state.include_price = True

def save_uploaded_file(uploaded_file):
    """Save uploaded file to temporary directory"""
    temp_dir = "data/output/temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    timestamp = int(time.time())
    file_extension = os.path.splitext(uploaded_file.name)[1]
    filename = f"upload_{timestamp}{file_extension}"
    file_path = os.path.join(temp_dir, filename)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# Sidebar - How to Use
with st.sidebar:
    st.markdown("## 📖 How to Use")
    st.markdown("---")
    st.markdown("""
    **1. Upload Image**  
    Select your product image file.
    
    **2. Process Image**  
    AI removes background and crops to 1:1 ratio.
    
    **3. Enter Details**  
    Provide product description, audience, and price.
    
    **4. Review Prompt**  
    Edit headline, footer, and offer text.
    
    **5. Generate Creative**  
    Get your premium Meta ad creative!
    """)
    
    st.markdown("---")
    if st.button("🔄 Reset Workflow", width='stretch'):
        reset_workflow()
        st.rerun()

# Main Header
st.markdown("<div style='text-align: center; margin-bottom: 3rem;'>", unsafe_allow_html=True)
st.title("🎨 Meta Ad Creative Generator")
st.markdown('<p class="subtitle">Transform your product images into premium Meta ad creatives powered by AI</p>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Workflow Step 1: Image Upload
if st.session_state.workflow_step == 'upload':
    st.markdown("### 📸 Step 1: Upload Product Image")
    st.markdown("Upload your product image to begin. Supported formats: PNG, JPG, JPEG, WEBP")
    
    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "**Choose an image file**",
        type=['png', 'jpg', 'jpeg', 'webp'],
        help="Upload your product image"
    )
    
    if uploaded_file is not None:
        image_path = save_uploaded_file(uploaded_file)
        st.session_state.image_path = image_path
        
        st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
        
        st.markdown("**Image Preview**")
        image = Image.open(uploaded_file)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(image, caption="Uploaded Image", width='stretch')
        st.session_state.uploaded_image = image
        
        st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Create Generative", width='stretch', type="primary"):
                st.session_state.workflow_step = 'processing'
                st.rerun()

# Workflow Step 2: Processing
elif st.session_state.workflow_step == 'processing':
    st.markdown("### ⚙️ Processing Image")
    st.markdown("Removing background and cropping your image to the perfect 1:1 ratio for Meta ads.")
    
    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Check if at least one API key is available
        bg_key = os.getenv("GOOGLE_API_KEY_BACKGROUND") or os.getenv("GOOGLE_API_KEY")
        if not bg_key:
            st.error("❌ Google API key not found. Please set GOOGLE_API_KEY_BACKGROUND or GOOGLE_API_KEY in your .env file.")
            st.stop()
        
        # Agent will automatically use GOOGLE_API_KEY_BACKGROUND or fall back to GOOGLE_API_KEY
        background_remover = BackgroundRemoverAgent()
        image_cropper = ImageCropperAgent()
        
        status_text.markdown("**🧹 Step 1/2:** Removing background...")
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
        
        status_text.markdown("**✂️ Step 2/2:** Cropping to 1:1 ratio...")
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
        status_text.markdown("**✅ Processing complete!**")
        
        st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
        st.success("✅ Image processed successfully!")
        
        st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Original Image**")
            st.image(st.session_state.image_path, width='stretch')
        
        with col2:
            st.markdown("**Processed Image**")
            cropped_image = Image.open(st.session_state.cropped_path)
            st.image(cropped_image, width='stretch')
        
        st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✅ Confirm & Generate Prompt", width='stretch', type="primary"):
                st.session_state.workflow_step = 'prompt_input'
                st.rerun()
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
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
    st.markdown("### 📝 Step 2: Product Details")
    st.markdown("Provide information about your product to generate the perfect ad creative.")
    
    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    
    if st.session_state.cropped_path:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("**Processed Image**")
            st.image(st.session_state.cropped_path, width=500)
    
    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    
    # Logo upload section - OUTSIDE the form (file uploaders don't work inside forms)
    st.markdown("**🏢 Company Logo (Optional)**")
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    
    include_logo = st.checkbox(
        "📎 Include Company Logo",
        value=st.session_state.logo_path is not None,
        help="Check to include your company logo at the top of the ad",
        key="include_logo_checkbox"
    )
    
    if include_logo:
        logo_file = st.file_uploader(
            "📎 Upload Company Logo",
            type=['png', 'jpg', 'jpeg'],
            help="Upload your company logo (PNG with transparency preferred)",
            key="logo_uploader"
        )
        
        if logo_file is not None:
            # Save logo to temp directory
            logo_dir = "data/output/temp"
            os.makedirs(logo_dir, exist_ok=True)
            
            # Use a consistent filename based on the uploaded file name
            logo_extension = os.path.splitext(logo_file.name)[1]
            logo_filename = f"company_logo{logo_extension}"
            logo_path = os.path.join(logo_dir, logo_filename)
            
            with open(logo_path, "wb") as f:
                f.write(logo_file.getbuffer())
            
            st.session_state.logo_path = logo_path
            
            # Show logo preview
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                logo_image = Image.open(logo_file)
                st.image(logo_image, caption="Logo Preview", width=150)
            
            st.success(f"✅ Logo uploaded successfully!")
        elif st.session_state.logo_path and os.path.exists(st.session_state.logo_path):
            # Show existing logo if already uploaded
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                st.image(st.session_state.logo_path, caption="Current Logo", width=150)
            st.info("ℹ️ Logo already uploaded. Upload a new one to replace it.")
    else:
        st.session_state.logo_path = None
    
    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    
    with st.form("product_details_form"):
        st.markdown("**Fill in the product information:**")
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        
        product_description = st.text_input(
            "📄 Product Description",
            placeholder="e.g., Premium wooden photo frame with mother-of-pearl inlay",
            help="Describe your product in detail"
        )
        
        target_audience = st.text_input(
            "👥 Target Audience",
            placeholder="e.g., Home decor enthusiasts, luxury buyers",
            help="Who is this product for?"
        )
        
        st.markdown("---")
        st.markdown("**🎨 Typography Settings**")
        
        primary_font = st.text_input(
            "📝 Primary Font (Required)",
            placeholder="e.g., Playfair Display, Calgary, Montserrat",
            help="Enter the exact font name you want to use for headlines and main text"
        )
        
        secondary_font = st.text_input(
            "📝 Secondary Font (Optional)",
            placeholder="e.g., Lato, Roboto, Tan Pearl",
            help="Enter font name for taglines and secondary text (leave empty to use primary font)"
        )
        
        include_price = st.checkbox(
            "💰 Include Price Tag",
            value=True,
            help="Check to include pricing information in the ad"
        )
        
        if include_price:
            price = st.text_input(
                "💰 Price Information",
                placeholder="e.g., before 2999 Rs after 1899 Rs",
                help="Original price and discounted price"
            )
            pricing_font = st.text_input(
                "📝 Pricing Font (Optional)",
                placeholder="e.g., RoxboroughCF, Montserrat Bold",
                help="Enter font name for pricing text (leave empty to use primary font in bold)"
            )
        else:
            price = ""
            pricing_font = ""
        
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
        
        # Show logo status in form
        if st.session_state.logo_path:
            st.info(f"🏢 Company logo will be included in the creative")
        
        submitted = st.form_submit_button("🚀 Generate Prompt", width='stretch', type="primary")
        
        if submitted:
            if not product_description or not target_audience:
                st.warning("⚠️ Please fill in product description and target audience")
            elif not primary_font:
                st.warning("⚠️ Please provide a primary font name")
            elif include_price and not price:
                st.warning("⚠️ Please provide price information if price tag is enabled")
            else:
                st.session_state.workflow_step = 'generating_prompt'
                st.session_state.product_description = product_description
                st.session_state.target_audience = target_audience
                st.session_state.price = price if include_price else ""
                st.session_state.primary_font = primary_font
                st.session_state.secondary_font = secondary_font if secondary_font else None
                st.session_state.pricing_font = pricing_font if (include_price and pricing_font) else None
                st.session_state.include_price = include_price
                st.rerun()
    
    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔙 Go Back", width='stretch'):
            st.session_state.workflow_step = 'processing'
            st.rerun()

# Workflow Step 4: Generating Prompt
elif st.session_state.workflow_step == 'generating_prompt':
    st.markdown("### 🤖 Generating Prompt")
    st.markdown("Analyzing your product and creating a structured prompt for the AI model.")
    
    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.markdown("**🎯 Analyzing product and generating structured prompt...**")
    progress_bar.progress(50)
    
    try:
        # Agent will automatically use GOOGLE_API_KEY_PROMPT or fall back to GOOGLE_API_KEY
        prompt_generator = PromptGeneratorAgent()
        
        user_inputs = {
            "target_audience": st.session_state.target_audience,
            "price": st.session_state.price if st.session_state.include_price else None
        }
        
        prompt_result = prompt_generator.generate_prompt(
            st.session_state.cropped_path,
            st.session_state.product_description,
            user_inputs,
            primary_font=st.session_state.primary_font,
            secondary_font=st.session_state.secondary_font,
            pricing_font=st.session_state.pricing_font,
            include_price=st.session_state.include_price,
            logo_path=st.session_state.logo_path
        )
        
        if not prompt_result["success"]:
            st.error(f"❌ Prompt generation failed: {prompt_result.get('error', 'Unknown error')}")
            if st.button("🔙 Go Back"):
                st.session_state.workflow_step = 'prompt_input'
                st.rerun()
            st.stop()
        
        generated_prompt = prompt_result["prompt"]
        if generated_prompt.startswith('```json'):
            generated_prompt = generated_prompt[7:]
        if generated_prompt.endswith('```'):
            generated_prompt = generated_prompt[:-3]
        generated_prompt = generated_prompt.strip()
        
        st.session_state.prompt = generated_prompt
        progress_bar.progress(100)
        status_text.markdown("**✅ Prompt generated!**")
        
        st.session_state.workflow_step = 'prompt_review'
        st.rerun()
    
    except Exception as e:
        st.error(f"❌ Error generating prompt: {str(e)}")
        if st.button("🔙 Go Back"):
            st.session_state.workflow_step = 'prompt_input'
            st.rerun()

# Workflow Step 5: Prompt Review
elif st.session_state.workflow_step == 'prompt_review':
    st.markdown("### 📋 Step 3: Review & Edit Prompt")
    st.markdown("Review and customize the generated text elements for your ad creative.")
    
    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    
    if st.session_state.prompt:
        try:
            prompt_json = json.loads(st.session_state.prompt)
            
            # Extract text elements from new structure
            text_elements = prompt_json.get("typography_and_layout", {}).get("text_elements", [])
            
            # Find headline, tagline, and CTA
            headline = ""
            tagline = ""
            cta_text = ""
            limited_offer = ""
            
            for element in text_elements:
                if element.get("type") == "text":
                    if element.get("hierarchy") == "primary":
                        headline = element.get("text", "")
                    elif element.get("hierarchy") == "secondary":
                        tagline = element.get("text", "")
                elif element.get("type") == "cta_button":
                    cta_text = element.get("text", "")
            
            # Check for limited offer in pricing section
            limited_offer_obj = prompt_json.get("typography_and_layout", {}).get("limited_time_offer")
            if limited_offer_obj:
                limited_offer = limited_offer_obj.get("text", "")
            
            st.markdown("**✏️ Edit Text Elements**")
            st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
            
            edited_headline = st.text_input("📰 Headline", value=headline)
            edited_tagline = st.text_input("📝 Tagline", value=tagline)
            edited_cta = st.text_input("🔘 Call-to-Action Button", value=cta_text)
            
            if st.session_state.include_price:
                edited_offer = st.text_input("⏰ Limited Time Offer", value=limited_offer)
            else:
                edited_offer = ""
            
            # Update JSON if edited
            updated = False
            for i, element in enumerate(text_elements):
                if element.get("type") == "text":
                    if element.get("hierarchy") == "primary" and edited_headline != headline:
                        text_elements[i]["text"] = edited_headline
                        updated = True
                    elif element.get("hierarchy") == "secondary" and edited_tagline != tagline:
                        text_elements[i]["text"] = edited_tagline
                        updated = True
                elif element.get("type") == "cta_button" and edited_cta != cta_text:
                    text_elements[i]["text"] = edited_cta
                    updated = True
            
            if st.session_state.include_price and edited_offer != limited_offer:
                if limited_offer_obj:
                    prompt_json["typography_and_layout"]["limited_time_offer"]["text"] = edited_offer
                    updated = True
            
            if updated:
                prompt_json["typography_and_layout"]["text_elements"] = text_elements
                st.session_state.prompt = json.dumps(prompt_json, indent=2)
            
            st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
            st.markdown("**📄 Full Prompt (JSON)**")
            
            with st.expander("View Full Prompt JSON"):
                st.code(st.session_state.prompt, language="json")
            
            st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
            
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
            
            st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Confirm & Generate Creative", width='stretch', type="primary"):
                    st.session_state.workflow_step = 'generating_creative'
                    st.rerun()
            
            with col2:
                if st.button("🔙 Go Back", width='stretch'):
                    st.session_state.workflow_step = 'prompt_input'
                    st.rerun()

# Workflow Step 6: Generating Creative
elif st.session_state.workflow_step == 'generating_creative':
    st.markdown("### 🎨 Generating Final Creative")
    st.markdown("Creating your premium Meta ad creative with AI. This may take a moment...")
    
    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.markdown("**🎯 Generating Meta ad creative with Nano Banana...**")
    progress_bar.progress(50)
    
    try:
        # Agent will automatically use GOOGLE_API_KEY_CREATIVE or fall back to GOOGLE_API_KEY
        creative_generator = CreativeGeneratorAgent()
        
        # Collect font names to strip from prompt
        font_names_to_strip = []
        if st.session_state.primary_font:
            font_names_to_strip.append(st.session_state.primary_font)
        if st.session_state.secondary_font:
            font_names_to_strip.append(st.session_state.secondary_font)
        if st.session_state.pricing_font:
            font_names_to_strip.append(st.session_state.pricing_font)
        
        creative_result = creative_generator.generate_creative(
            st.session_state.cropped_path,
            st.session_state.prompt,
            st.session_state.product_description,
            logo_path=st.session_state.logo_path,
            font_names=font_names_to_strip if font_names_to_strip else None
        )
        
        if not creative_result["success"]:
            st.error(f"❌ Creative generation failed: {creative_result.get('error', 'Unknown error')}")
            if st.button("🔙 Go Back"):
                st.session_state.workflow_step = 'prompt_review'
                st.rerun()
            st.stop()
        
        st.session_state.final_creative_path = creative_result["output_path"]
        progress_bar.progress(100)
        status_text.markdown("**✅ Creative generated!**")
        
        st.session_state.workflow_step = 'complete'
        st.rerun()
    
    except Exception as e:
        st.error(f"❌ Error generating creative: {str(e)}")
        if st.button("🔙 Go Back"):
            st.session_state.workflow_step = 'prompt_review'
            st.rerun()

# Workflow Step 7: Complete
elif st.session_state.workflow_step == 'complete':
    st.markdown("### 🎉 Your Meta Ad Creative is Ready!")
    st.markdown("Your premium ad creative has been generated successfully. Download it below!")
    
    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    
    if st.session_state.final_creative_path and os.path.exists(st.session_state.final_creative_path):
        final_image = Image.open(st.session_state.final_creative_path)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(final_image, caption="Final Meta Ad Creative", width='stretch')
        
        st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
        
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
        
        st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
        
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
