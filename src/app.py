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
from agents.product_analyser import ProductAnalyserAgent
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
if 'product_persona' not in st.session_state:
    st.session_state.product_persona = None
if 'ai_analysis' not in st.session_state:
    st.session_state.ai_analysis = None
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
if 'include_price' not in st.session_state:
    st.session_state.include_price = False
if 'promotion_text' not in st.session_state:
    st.session_state.promotion_text = None

def reset_workflow():
    """Reset the workflow to start over"""
    st.session_state.workflow_step = 'upload'
    st.session_state.product_persona = None
    st.session_state.ai_analysis = None
    st.session_state.white_bg_path = None
    st.session_state.cropped_path = None
    st.session_state.prompt = None
    st.session_state.final_creative_path = None
    st.session_state.logo_path = None
    st.session_state.include_price = False
    st.session_state.promotion_text = None

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
    
    **2. Analyze Product (Agent 1)**  
    AI analyzes your product and collects product information.
    
    **3. Process Image (Agent 2)**  
    AI removes background and crops to 1:1 ratio.
    
    **4. Configure Ad (Agent 3 Setup)**  
    Set logo, promotion, price, and fonts.
    
    **5. Generate Prompt (Agent 3)**  
    AI creates structured prompt for ad generation.
    
    **6. Generate Creative (Agent 4)**  
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
            if st.button("🔍 Analyze Product", width='stretch', type="primary"):
                st.session_state.workflow_step = 'product_analysis'
                st.rerun()

# Workflow Step 2: Product Analysis (Agent 1)
elif st.session_state.workflow_step == 'product_analysis':
    st.markdown("### 🤖 Agent 1: Professional Product Analyser")
    st.markdown("Analyzing your product image and collecting product information.")
    
    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    
    # Step 2a: AI Analysis
    if st.session_state.ai_analysis is None:
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.markdown("**🔍 Analyzing product image with AI...**")
        progress_bar.progress(30)
        
        try:
            # Check if API key is available
            analyser_key = os.getenv("GOOGLE_API_KEY_ANALYSER") or os.getenv("GOOGLE_API_KEY")
            if not analyser_key:
                st.error("❌ Google API key not found. Please set GOOGLE_API_KEY_ANALYSER or GOOGLE_API_KEY in your .env file.")
                st.stop()
            
            product_analyser = ProductAnalyserAgent()
            analysis_result = product_analyser.analyze_product(st.session_state.image_path)
            
            if not analysis_result["success"]:
                st.error(f"❌ Product analysis failed: {analysis_result.get('error', 'Unknown error')}")
                if st.button("🔙 Go Back"):
                    st.session_state.workflow_step = 'upload'
                    st.rerun()
                st.stop()
            
            st.session_state.ai_analysis = analysis_result
            progress_bar.progress(100)
            status_text.markdown("**✅ Product analysis complete!**")
            
        except Exception as e:
            st.error(f"❌ Error during product analysis: {str(e)}")
            if st.button("🔙 Go Back"):
                st.session_state.workflow_step = 'upload'
                st.rerun()
            st.stop()
    
    # Display AI Analysis Results
    if st.session_state.ai_analysis:
        st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
        st.success("✅ AI Analysis Complete!")
        
        structured = st.session_state.ai_analysis.get("structured_analysis", {})
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📊 AI Analysis Results**")
            st.markdown(f"**Product Type:** {structured.get('product_type', 'Not detected')}")
            st.markdown(f"**Materials:** {', '.join(structured.get('materials', [])) if structured.get('materials') else 'Not detected'}")
            st.markdown(f"**Style:** {structured.get('style', 'Not detected')}")
        
        with col2:
            st.markdown("**🔍 Key Features**")
            features = structured.get('features', [])
            if features:
                for feature in features[:5]:  # Show first 5 features
                    st.markdown(f"- {feature}")
            else:
                st.markdown("No features detected")
        
        st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
        
        # Step 2b: Collect User Inputs
        st.markdown("### 📝 Provide Product Information")
        st.markdown("Please fill in the details about your product:")
        
        with st.form("product_info_form"):
            product_name = st.text_input(
                "📦 Product Name",
                placeholder="e.g., Premium Wooden Photo Frame",
                help="Enter the name of your product"
            )
            
            product_usp = st.text_area(
                "💡 Product USP / Use Case",
                placeholder="e.g., Handcrafted photo frame with mother-of-pearl inlay, perfect for displaying cherished memories",
                help="Describe what makes your product unique and how it's used",
                height=100
            )
            
            target_audience = st.text_input(
                "👥 Target Audience",
                placeholder="e.g., Home decor enthusiasts, luxury buyers, gift givers",
                help="Who is this product for?"
            )
            
            st.markdown("---")
            st.markdown("**💰 Promotion Details**")
            
            include_promotion = st.checkbox(
                "🎯 Include Promotion",
                value=False,
                help="Check if you want to include a promotion in the ad"
            )
            
            promotion_percentage = None
            before_price = ""
            after_price = ""
            
            if include_promotion:
                col1, col2 = st.columns(2)
                with col1:
                    promotion_percentage = st.number_input(
                        "📊 Promotion Percentage",
                        min_value=0,
                        max_value=100,
                        value=30,
                        help="Discount percentage (e.g., 30 for 30% off)"
                    )
                    before_price = st.text_input(
                        "💰 Original Price",
                        placeholder="e.g., Rs. 2999",
                        help="Price before discount"
                    )
                with col2:
                    after_price = st.text_input(
                        "💰 Discounted Price",
                        placeholder="e.g., Rs. 1899",
                        help="Price after discount"
                    )
            
            additional_comments = st.text_area(
                "📝 Additional Comments",
                placeholder="Any additional information or specific requirements for the ad creative",
                help="Optional: Add any specific requirements or notes",
                height=80
            )
            
            submitted = st.form_submit_button("💾 Save Product Info & Continue", width='stretch', type="primary")
            
            if submitted:
                if not product_usp or not target_audience:
                    st.warning("⚠️ Please fill in Product USP and Target Audience")
                else:
                    # Create user inputs dictionary
                    user_inputs = {
                        "product_name": product_name,
                        "usp": product_usp,
                        "target_audience": target_audience,
                        "promotion": {
                            "included": include_promotion,
                            "percentage": promotion_percentage if include_promotion else 0,
                            "before_price": before_price if include_promotion else "",
                            "after_price": after_price if include_promotion else ""
                        },
                        "additional_comments": additional_comments
                    }
                    
                    # Create product persona
                    product_analyser = ProductAnalyserAgent()
                    product_persona = product_analyser.create_product_persona(
                        st.session_state.ai_analysis,
                        user_inputs
                    )
                    
                    st.session_state.product_persona = product_persona
                st.session_state.workflow_step = 'processing'
                st.rerun()

        st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔙 Go Back", width='stretch'):
                st.session_state.workflow_step = 'upload'
                st.rerun()

# Workflow Step 3: Background Removal & Cropping (Agent 2)
elif st.session_state.workflow_step == 'processing':
    st.markdown("### ⚙️ Agent 2: Background Remover + Cropper")
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
            st.info("💡 Tip: This can happen if the AI model didn't generate an image. Please try again.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Retry", key="retry_bg"):
                    st.rerun()
            with col2:
                if st.button("🔙 Go Back", key="back_bg"):
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
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Retry", key="retry_crop"):
                    st.rerun()
            with col2:
                if st.button("🔙 Go Back", key="back_crop"):
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
            if st.button("✅ Confirm & Continue to Prompt Setup", width='stretch', type="primary"):
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

# Workflow Step 4: Prompt Generation Setup (Agent 3 Inputs)
elif st.session_state.workflow_step == 'prompt_input':
    st.markdown("### ⚙️ Agent 3 Setup: Configure Ad Creative")
    st.markdown("Configure logo, promotion, pricing, and typography for your ad creative.")
    
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
    
    # Check if promotion is included in product persona
    promotion_included = False
    if st.session_state.product_persona:
        promotion_data = st.session_state.product_persona.get("user_inputs", {}).get("promotion", {})
        promotion_included = promotion_data.get("included", False)
    
    with st.form("prompt_setup_form"):
        st.markdown("**Configure ad creative settings:**")
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        
        # Promotion text input (if promotion is included)
        if promotion_included:
            st.markdown("**🎯 Promotion**")
            promotion_text = st.text_input(
                "📢 Promotion Text",
                value=st.session_state.promotion_text or "",
                placeholder="e.g., 30% Winter Sale, Limited Time Offer, Flash Sale",
                help="Enter the promotion text to display in the ad"
            )
            st.session_state.promotion_text = promotion_text
            st.markdown("---")
        
        # Pricing temporarily disabled in UI (handled by backend defaults)
        include_price = False
        
        st.markdown("---")
        st.markdown("**🎨 Typography**")
        
        # Display detected font styles from product analysis
        if st.session_state.product_persona:
            font_styles = st.session_state.product_persona.get("ai_analysis", {}).get("font_styles", {})
            product_style = st.session_state.product_persona.get("ai_analysis", {}).get("style", "")
            
            if font_styles:
                st.success(f"✨ **AI-Selected Typography** based on product style: *{product_style or 'Professional'}*")
                with st.expander("📝 View Font Style Details", expanded=False):
                    st.markdown(f"**Headline:** {font_styles.get('headline', 'Professional serif')[:100]}...")
                    st.markdown(f"**Tagline:** {font_styles.get('tagline', 'Clean sans-serif')[:100]}...")
                    st.markdown(f"**CTA Button:** {font_styles.get('cta', 'Medium-weight sans-serif')[:80]}...")
        else:
            st.info("🎨 Font styles will be automatically selected based on your product's aesthetic")
        
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
        
        # Show logo status in form
        if st.session_state.logo_path:
            st.info(f"🏢 Company logo will be included in the creative")
        
        submitted = st.form_submit_button("🚀 Generate Prompt", width='stretch', type="primary")
        
        if submitted:
            # Font styles are auto-detected from product analysis
            st.session_state.workflow_step = 'generating_prompt'
            st.session_state.include_price = False
            st.rerun()
    
    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔙 Go Back", width='stretch'):
            st.session_state.workflow_step = 'processing'
            st.rerun()

# Workflow Step 5: Prompt Generation (Agent 3)
elif st.session_state.workflow_step == 'generating_prompt':
    st.markdown("### 🤖 Agent 3: Prompt Generator")
    st.markdown("Creating a structured prompt for the AI model based on your product information.")
    
    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.markdown("**🎯 Analyzing product and generating structured prompt...**")
    progress_bar.progress(50)
    
    try:
        # Agent will automatically use GOOGLE_API_KEY_PROMPT or fall back to GOOGLE_API_KEY
        prompt_generator = PromptGeneratorAgent()
        
        # Use product_persona - font styles are automatically detected from product analysis
        prompt_result = prompt_generator.generate_prompt(
            st.session_state.cropped_path,
            product_persona=st.session_state.product_persona,
            include_price=st.session_state.include_price,
            logo_path=st.session_state.logo_path,
            promotion_text=st.session_state.promotion_text
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

# Workflow Step 5b: Prompt Review
elif st.session_state.workflow_step == 'prompt_review':
    st.markdown("### 📋 Review & Edit Prompt")
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

# Workflow Step 6: Creative Generation (Agent 4)
elif st.session_state.workflow_step == 'generating_creative':
    st.markdown("### 🎨 Agent 4: Ad Generator")
    st.markdown("Creating your premium Meta ad creative with AI. This may take a moment...")
    
    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.markdown("**🎯 Generating Meta ad creative with Nano Banana Pro/Nano Banana...**")
    progress_bar.progress(50)
    
    try:
        # Agent will automatically use GOOGLE_API_KEY_CREATIVE or fall back to GOOGLE_API_KEY
        creative_generator = CreativeGeneratorAgent()
        
        # Get product description from persona if available
        product_description = ""
        if st.session_state.product_persona:
            product_description = st.session_state.product_persona.get("user_inputs", {}).get("usp", "")
        
        # Font styles are now descriptive (not specific names), so no stripping needed
        creative_result = creative_generator.generate_creative(
            st.session_state.cropped_path,
            st.session_state.prompt,
            product_description=product_description,
            logo_path=st.session_state.logo_path,
            font_names=None,  # No specific font names to strip - using descriptive styles
            include_price=st.session_state.include_price
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
