import streamlit as st
import requests
import hashlib
import pymongo
import re
from PIL import Image
import io
import time

# Page configuration
st.set_page_config(
    page_title="MediScan - Medical Image Analysis",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern UI matching React design
st.markdown("""
<style>
    /* Global styles */
    .stApp {
        background: url('file:///C:/Users/mostafa/Desktop/photo_2025-12-09_03-05-18.jpg') no-repeat center center fixed;
        background-size: cover;
        position: relative;
    }
    
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(4, 8, 15, 0.7);
        z-index: 0;
    }
    
    .stApp > div {
        position: relative;
        z-index: 1;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom containers */
    .glass-container {
        background: rgba(4, 8, 15, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 2rem;
        border: 1px solid rgba(20, 33, 61, 0.3);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    
    .auth-container {
        max-width: 500px;
        margin: 0 auto;
        margin-top: 5vh;
    }
    
    .header-gradient {
        background: #14213d;
        padding: 2rem;
        border-radius: 24px 24px 0 0;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .brain-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        filter: grayscale(20%);
    }
    
    .title-text {
        color: white;
        font-size: 2rem;
        font-weight: bold;
        margin: 0;
    }
    
    .subtitle-text {
        color: rgba(255, 255, 255, 0.7);
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    
    /* Buttons */
    .stButton > button {
        width: 100%;
        background: #14213d;
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        font-weight: bold;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 20px rgba(20, 33, 61, 0.5);
        background: #1a2950;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background: #04080f;
        border: 1px solid rgba(20, 33, 61, 0.5);
        border-radius: 12px;
        color: white;
        padding: 0.75rem 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #14213d;
        box-shadow: 0 0 0 2px rgba(20, 33, 61, 0.3);
    }
    
    /* Labels */
    .stTextInput > label {
        color: rgba(255, 255, 255, 0.8) !important;
        font-weight: 500;
    }
    
    /* Upload area */
    .uploadedFile {
        background: rgba(20, 33, 61, 0.3);
        border-radius: 16px;
        padding: 1rem;
    }
    
    /* Results card */
    .result-card {
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        color: white;
    }
    
    .result-normal {
        background: #14213d;
    }
    
    .result-pneumonia {
        background: #14213d;
    }
    
    .result-tuberculosis {
        background: #14213d;
    }
    
    .result-unknown {
        background: #14213d;
    }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background: #14213d;
    }
    
    /* Success/Error messages */
    .stAlert {
        border-radius: 12px;
    }
    
    /* Feature cards */
    .feature-card {
        background: rgba(4, 8, 15, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(20, 33, 61, 0.5);
        text-align: center;
        height: 100%;
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        color: white;
        font-weight: bold;
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }
    
    .feature-text {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.9rem;
    }
    
    /* Main title */
    .main-title {
        color: white;
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .main-subtitle {
        color: rgba(255, 255, 255, 0.8);
        font-size: 1.3rem;
        text-align: center;
        margin-bottom: 3rem;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(20, 33, 61, 0.3);
        border-radius: 12px;
        color: rgba(255, 255, 255, 0.6);
        padding: 0.5rem 2rem;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: #14213d;
        color: white;
    }
    
    /* Info box */
    .info-box {
        background: rgba(20, 33, 61, 0.5);
        border: 1px solid rgba(20, 33, 61, 0.7);
        border-radius: 12px;
        padding: 1rem;
        color: rgba(255, 255, 255, 0.9);
        margin-top: 1rem;
    }
    
    /* Probability bars */
    .prob-container {
        margin: 1rem 0;
    }
    
    .prob-label {
        display: flex;
        justify-content: space-between;
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    .prob-bar-bg {
        background: rgba(255, 255, 255, 0.2);
        height: 12px;
        border-radius: 6px;
        overflow: hidden;
    }
    
    .prob-bar-fill {
        height: 100%;
        border-radius: 6px;
        transition: width 1s ease-in-out;
        background: white;
    }
    
    /* Chatbot button */
    .chatbot-btn {
        background: linear-gradient(135deg, #14213d 0%, #1a2950 100%) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 50% !important;
        width: 90px !important;
        height: 90px !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        box-shadow: 0 0 10px #14213d, 0 0 20px #fff, 0 0 10px #1a2950;
        margin-top: 10px !important;
        margin-bottom: 8px !important;
        letter-spacing: 1px;
        text-shadow: 0 0 6px #fff, 0 0 10px #14213d;
        transition: all 0.2s;
        animation: chatbotfire 1.2s infinite alternate;
        cursor: pointer;
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 0.2em;
        padding: 0 !important;
    }
    
    .chatbot-btn__icon {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        vertical-align: middle;
        display: block;
        margin-bottom: 2px;
    }
    
    .chatbot-btn__text {
        font-size: 1.05rem;
        font-weight: bold;
        color: #fff;
        margin: 0;
        padding: 0;
        text-align: center;
        line-height: 1.1;
        letter-spacing: 1px;
        text-shadow: 0 0 6px #fff, 0 0 10px #14213d;
    }
    
    .chatbot-btn:hover {
        background: linear-gradient(135deg, #1a2950 0%, #14213d 100%) !important;
        color: #fff !important;
        box-shadow: 0 0 20px #1a2950, 0 0 40px #fff, 0 0 10px #14213d;
        transform: scale(1.08) rotate(-2deg);
        border: 2px solid #fff !important;
    }
    
    @keyframes chatbotfire {
        0% { box-shadow: 0 0 10px #14213d, 0 0 20px #fff, 0 0 10px #1a2950;}
        100% { box-shadow: 0 0 20px #1a2950, 0 0 40px #fff, 0 0 20px #14213d;}
    }
</style>
""", unsafe_allow_html=True)

# Configuration
API_URL = "http://127.0.0.1:5000/predict"
MONGODB_URI = "mongodb+srv://projectDB:PEyHwQ2fF7e5saEf@cluster0.43hxo.mongodb.net/"
DB_NAME = "ta7t-bety"
COLLECTION_NAME = "paitents"

# MongoDB connection
@st.cache_resource
def init_db():
    """Initialize MongoDB connection"""
    try:
        client = pymongo.MongoClient(MONGODB_URI)
        db = client[DB_NAME]
        # Test connection
        client.server_info()
        return db[COLLECTION_NAME]
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        return None

# Helper functions
def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def is_valid_email(email):
    """Validate email format (must be Gmail)"""
    gmail_pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
    return re.match(gmail_pattern, email) is not None

def register_user(collection, name, email, password):
    """Register a new user in MongoDB"""
    if collection is None:
        return False, "Failed to connect to database"
    
    # Validate email format
    if not is_valid_email(email):
        return False, "Please use a valid Gmail address (****@gmail.com)"
    
    try:
        # Check if email already exists
        if collection.find_one({"email": email}):
            return False, "Email already in use"
        
        # Create user document
        user_data = {
            "name": name,
            "email": email,
            "password": hash_password(password),
            "created_at": time.time()
        }
        
        # Insert into MongoDB
        collection.insert_one(user_data)
        return True, "User registered successfully"
    except Exception as e:
        return False, f"Registration failed: {str(e)}"

def verify_user(collection, email, password):
    """Verify user credentials from MongoDB"""
    if collection is None:
        return False, None
    
    try:
        hashed_password = hash_password(password)
        user = collection.find_one({"email": email, "password": hashed_password})
        
        if user:
            return True, {"name": user['name'], "email": user['email']}
        return False, None
    except Exception as e:
        st.error(f"Login failed: {e}")
        return False, None

def get_condition_color(condition):
    """Get color class for condition"""
    colors = {
        "NORMAL": "result-normal",
        "PNEUMONIA": "result-pneumonia",
        "TUBERCULOSIS": "result-tuberculosis",
        "UNKNOWN": "result-unknown"
    }
    return colors.get(condition, "result-normal")

def get_gradient_color(condition):
    """Get gradient color for progress bars"""
    return "#14213d"

# Initialize MongoDB connection
collection = init_db()

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'selected_image' not in st.session_state:
    st.session_state.selected_image = None
if 'result' not in st.session_state:
    st.session_state.result = None
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0

# Authentication Screen
if not st.session_state.authenticated:
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown("""
        <div class="glass-container">
            <div class="header-gradient">
                <div class="brain-icon">🔬</div>
                <h1 class="title-text">MediScan</h1>
                <p class="subtitle-text">Medical Image Analysis Platform</p>
            </div>
    """, unsafe_allow_html=True)
    
    # Check database connection
    if collection is None:
        st.error("Cannot connect to database. Please check your connection.")
        st.stop()
    
    # Tabs for Login/Register
    if st.session_state.active_tab == 0:
        tab_names = ["Login", "Register"]
    else:
        tab_names = ["Register", "Login"]
    
    tab1, tab2 = st.tabs(tab_names)
    
    # Show login tab
    with (tab1 if st.session_state.active_tab == 0 else tab2):
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("Please use your Gmail account to log in")
        
        email = st.text_input("Email Address", key="login_email", placeholder="your.email@gmail.com")
        password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
        
        if st.button("Sign In", key="login_btn"):
            if email and password:
                success, user_data = verify_user(collection, email, password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user = user_data
                    st.success("Login successful!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid email or password. Please register if you don't have an account.")
            else:
                st.error("Please fill in all fields")
    
    # Show register tab
    with (tab2 if st.session_state.active_tab == 0 else tab1):
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("Create an account using your Gmail address")
        
        name = st.text_input("Full Name", key="register_name", placeholder="Enter your full name")
        email = st.text_input("Email Address", key="register_email", placeholder="your.email@gmail.com")
        password = st.text_input("Password", type="password", key="register_password", placeholder="Create a strong password")
        confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm_password", placeholder="Re-enter your password")
        
        if st.button("Create Account", key="register_btn"):
            if name and email and password and confirm_password:
                # Check if passwords match
                if password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    success, message = register_user(collection, name, email, password)
                    if success:
                        st.success(message)
                        st.success("Account created successfully! Redirecting to login...")
                        st.session_state.active_tab = 0
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.error("Please fill in all fields")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
        <div style="text-align: center; margin-top: 2rem; color: rgba(255, 255, 255, 0.6);">
            <p>Secure  |  HIPAA Compliant  |  Gmail Required</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Main Application Screen
else:
    # Navbar
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="width: 50px; height: 50px; background: #14213d; 
                            border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem;">
                    🔬
                </div>
                <h2 style="color: white; margin: 0; font-size: 1.5rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">MediScan</h2>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: flex-end; gap: 1rem;">
                <span style="color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">{st.session_state.user['name']}</span>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Logout", key="logout_btn"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.selected_image = None
            st.session_state.result = None
            st.success("Logged out successfully")
            time.sleep(1)
            st.rerun()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Main Title
    st.markdown('<h1 class="main-title">Chest X-Ray Analysis</h1>', unsafe_allow_html=True)
    st.markdown('<p class="main-subtitle">Deep learning based medical diagnosis</p>', unsafe_allow_html=True)
    
    # Two Column Layout
    col_left, col_right = st.columns(2, gap="large")
    
    with col_left:
        st.markdown("""
            <div class="glass-container">
                <h2 style="color: white; margin-bottom: 1.5rem;">Upload X-Ray Image</h2>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose an X-ray image",
            type=['png', 'jpg', 'jpeg'],
            help="Upload a chest X-ray image for analysis",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            st.session_state.selected_image = uploaded_file
            image = Image.open(uploaded_file)
            st.image(image, use_column_width=True, caption="Selected X-Ray Image")
        else:
            st.markdown("""
                <div style="border: 2px dashed rgba(255, 255, 255, 0.3); border-radius: 16px; 
                            padding: 3rem; text-align: center; color: rgba(255, 255, 255, 0.7);">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">+</div>
                    <p style="font-size: 1.1rem;">Drop your X-ray image here</p>
                    <p style="font-size: 0.9rem;">or click to browse</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Analyze Image", disabled=uploaded_file is None, use_container_width=True):
            with st.spinner("Analyzing image..."):
                try:
                    # Reset file pointer to beginning
                    uploaded_file.seek(0)
                    
                    # Prepare files for API request
                    files = {'image': (uploaded_file.name, uploaded_file, uploaded_file.type)}
                    
                    # Make API request
                    response = requests.post(API_URL, files=files, timeout=30)
                    
                    if response.status_code == 200:
                        st.session_state.result = response.json()
                        st.success("Analysis complete")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        error_msg = response.json().get('error', 'Unknown error') if response.headers.get('content-type') == 'application/json' else response.text
                        st.error(f"Analysis failed: {error_msg}")
                        
                except requests.exceptions.ConnectionError:
                    st.error(f"Cannot connect to API at {API_URL}. Make sure the Flask server is running.")
                except requests.exceptions.Timeout:
                    st.error("Request timeout. The server took too long to respond.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_right:
        st.markdown("""
            <div class="glass-container">
                <h2 style="color: white; margin-bottom: 1.5rem;">Diagnosis Results</h2>
        """, unsafe_allow_html=True)
        
        if st.session_state.result:
            result = st.session_state.result
            predicted_class = result['predicted_class']
            probabilities = result['probabilities']
            
            # Primary diagnosis card
            color_class = get_condition_color(predicted_class)
            st.markdown(f"""
                <div class="result-card {color_class}">
                    <p style="opacity: 0.8; margin-bottom: 0.5rem;">Primary Diagnosis</p>
                    <h1 style="font-size: 2rem; margin: 0.5rem 0;">{predicted_class}</h1>
                    <p style="opacity: 0.9;">Confidence: {probabilities[predicted_class]*100:.2f}%</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Detailed probabilities
            st.markdown('<p style="color: white; font-weight: bold; margin: 1.5rem 0 1rem 0;">Detailed Probabilities</p>', unsafe_allow_html=True)
            
            for condition, prob in probabilities.items():
                st.markdown(f"""
                    <div class="prob-container">
                        <div class="prob-label">
                            <span>{condition}</span>
                            <span>{prob*100:.2f}%</span>
                        </div>
                        <div class="prob-bar-bg">
                            <div class="prob-bar-fill" style="width: {prob*100}%; background: white;"></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Disclaimer
            st.markdown("""
                <div class="info-box">
                    <strong>Disclaimer:</strong> This analysis is for informational purposes only. 
                    Always consult with a qualified healthcare professional for medical diagnosis and treatment.
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="text-align: center; padding: 3rem 0; color: rgba(255, 255, 255, 0.7);">
                    <div style="font-size: 4rem; margin-bottom: 1rem;">...</div>
                    <p style="font-size: 1.1rem;">Upload and analyze an X-ray<br>image to see results</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Feature Cards
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    feat_col1, feat_col2, feat_col3 = st.columns(3, gap="large")
    
    with feat_col1:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🔬</div>
                <h3 class="feature-title">Deep Learning</h3>
                <p class="feature-text">Powered by ResNet-18 architecture trained on medical datasets</p>
            </div>
        """, unsafe_allow_html=True)
    
    with feat_col2:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🔒</div>
                <h3 class="feature-title">Secure & Private</h3>
                <p class="feature-text">Your medical data is processed securely with end-to-end encryption</p>
            </div>
        """, unsafe_allow_html=True)
    
    with feat_col3:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <h3 class="feature-title">Instant Results</h3>
                <p class="feature-text">Get immediate analysis with detailed probability metrics</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Add "Need More Help?" section with chatbot button
    st.markdown("---")
    st.markdown('<h2 style="color: white; text-align: center; margin-bottom: 2rem;">Need More Help?</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
            <div style="background: rgba(4, 8, 15, 0.9); border-radius: 16px; padding: 2rem; color: white;">
                <h3>🤖 Questions about Medical Results?</h3>
                <p><strong>Frequently Asked Questions:</strong></p>
                <ul>
                    <li>How to get the best results?</li>
                    <li>What to do with the results?</li>
                    <li>Understanding your diagnosis</li>
                    <li>Next steps for treatment</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style="background: rgba(4, 8, 15, 0.9); border-radius: 16px; padding: 2rem; text-align: center;">
                <h3 style="color: white; margin-bottom: 1.5rem;">Chat with AI Assistant</h3>
                <a href="https://share.chatling.ai/s/VGP4VX6SgTltNqQ" target="_blank" style="text-decoration:none;">
                    <button class="chatbot-btn">
                        <img src="https://cdn-icons-png.flaticon.com/512/4712/4712035.png" alt="Chatbot Logo" class="chatbot-btn__icon" />
                        <span class="chatbot-btn__text">Chatbot</span>
                    </button>
                </a>
                <p style="color: rgba(255, 255, 255, 0.7); margin-top: 1rem; font-size: 0.9rem;">
                    Get instant answers to your medical questions
                </p>
            </div>
        """, unsafe_allow_html=True)
