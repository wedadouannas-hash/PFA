import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, recall_score, f1_score, confusion_matrix, roc_auc_score, classification_report, precision_score
import pickle
import base64
from io import BytesIO
import mysql.connector
from mysql.connector import Error
import hashlib
import warnings
import os

warnings.filterwarnings('ignore')

# Set page configuration with Dark Orange theme
st.set_page_config(
    page_title="Orange Telecom - Churn Prediction",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database Configuration
DATABASE_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Wedad#03",
    "database": "orange_pfa",
    "port": 3306
}

# Enhanced Professional Dark Orange Theme CSS
st.markdown("""
    <style>
    /* Professional Dark Orange Theme - Enhanced */
    :root {
        --dark-bg: #0f172a;
        --dark-card: #1e293b;
        --dark-text: #ffffff;
        --dark-border: #334155;
        --orange-primary: #f97316;
        --orange-secondary: #ea580c;
        --orange-light: #fdba74;
        --orange-dark: #c2410c;
        --success: #10b981;
        --danger: #ef4444;
        --warning: #f59e0b;
        --info: #3b82f6;
        --gray-light: #94a3b8;
        --gray-lighter: #cbd5e1;
    }

    /* Improved Typography */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    }

    .stApp {
        background-color: var(--dark-bg);
        color: var(--dark-text);
        font-size: 14px;
        line-height: 1.5;
    }

    /* Professional Headers */
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--orange-primary);
        text-align: center;
        margin-bottom: 1rem;
        padding: 1rem;
        letter-spacing: -0.5px;
        background: linear-gradient(135deg, rgba(249, 115, 22, 0.1), rgba(234, 88, 12, 0.05));
        border-radius: 12px;
        border: 1px solid rgba(249, 115, 22, 0.2);
    }

    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--orange-light);
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--orange-primary);
        position: relative;
    }

    .section-header::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 60px;
        height: 2px;
        background: linear-gradient(90deg, var(--orange-primary), transparent);
    }

    .subsection-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--gray-lighter);
        margin: 1.5rem 0 0.75rem 0;
        padding-left: 0.5rem;
        border-left: 3px solid var(--orange-primary);
    }

    /* Improved Paragraph Text */
    p, .stMarkdown p {
        color: var(--gray-lighter);
        font-size: 14px;
        line-height: 1.6;
        margin-bottom: 0.75rem;
    }

    /* Enhanced Login Page */
    .login-container {
        max-width: 420px;
        margin: 3rem auto;
        padding: 2.5rem;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 20px;
        border: 1px solid var(--dark-border);
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.4);
        position: relative;
        overflow: hidden;
    }

    .login-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--orange-primary), var(--orange-secondary));
    }

    .login-title {
        font-size: 2rem;
        font-weight: 700;
        color: white;
        margin-bottom: 0.5rem;
        text-align: center;
    }

    .login-subtitle {
        font-size: 14px;
        color: var(--gray-light);
        text-align: center;
        margin-bottom: 2rem;
        line-height: 1.5;
    }

    /* Enhanced Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(45, 55, 72, 0.9));
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid var(--dark-border);
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
        backdrop-filter: blur(10px);
    }

    .metric-card:hover {
        transform: translateY(-2px);
        border-color: var(--orange-primary);
        box-shadow: 0 8px 25px rgba(249, 115, 22, 0.15);
    }

    .metric-card h3 {
        font-size: 14px;
        font-weight: 600;
        color: var(--gray-light);
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .metric-card h1 {
        font-size: 2.2rem;
        font-weight: 700;
        color: white;
        margin: 0.5rem 0;
    }

    .metric-card p {
        font-size: 12px;
        color: var(--gray-light);
        margin: 0;
    }

    /* Enhanced Prediction Cards */
    .prediction-high {
        background: linear-gradient(135deg, rgba(127, 29, 29, 0.2), rgba(153, 27, 27, 0.3));
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid var(--danger);
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }

    .prediction-high::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--danger), transparent);
    }

    .prediction-low {
        background: linear-gradient(135deg, rgba(6, 78, 59, 0.2), rgba(6, 95, 70, 0.3));
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid var(--success);
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }

    .prediction-low::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--success), transparent);
    }

    /* Enhanced Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--orange-primary), var(--orange-secondary));
        color: white;
        border: none;
        padding: 0.625rem 1.5rem;
        font-size: 14px;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.3s ease;
        width: 100%;
        position: relative;
        overflow: hidden;
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: 0.5s;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, var(--orange-secondary), var(--orange-dark));
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(249, 115, 22, 0.3);
    }

    .stButton > button:hover::before {
        left: 100%;
    }

    /* Enhanced Sidebar */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid var(--dark-border);
    }

    .user-info {
        background: linear-gradient(135deg, rgba(249, 115, 22, 0.1), rgba(234, 88, 12, 0.1));
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(249, 115, 22, 0.2);
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .user-info::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--orange-primary), var(--orange-secondary));
    }

    .user-info h4 {
        color: white;
        font-size: 1rem;
        font-weight: 600;
        margin: 0 0 0.25rem 0;
    }

    .user-info p {
        color: var(--gray-light);
        font-size: 12px;
        margin: 0;
    }

    /* Enhanced Form Elements */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div,
    .stSlider > div {
        background-color: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid var(--dark-border) !important;
        border-radius: 8px !important;
        color: white !important;
        font-size: 14px !important;
        padding: 0.5rem 0.75rem !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus {
        border-color: var(--orange-primary) !important;
        box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.1) !important;
        outline: none !important;
    }

    .stSelectbox label,
    .stTextInput label,
    .stNumberInput label {
        color: var(--gray-lighter) !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        margin-bottom: 0.25rem !important;
    }

    /* Enhanced Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background-color: transparent;
        border-bottom: 1px solid var(--dark-border);
        padding-bottom: 0;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        color: var(--gray-light);
        border: 1px solid transparent;
        font-size: 14px;
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(249, 115, 22, 0.1);
        color: var(--orange-light);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--orange-primary), var(--orange-secondary));
        color: white !important;
        border-color: var(--orange-primary);
        font-weight: 600;
        position: relative;
    }

    .stTabs [aria-selected="true"]::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--orange-primary);
    }

    /* Enhanced Feature Cards */
    .feature-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(45, 55, 72, 0.8));
        padding: 1.25rem;
        border-radius: 10px;
        border-left: 4px solid var(--orange-primary);
        margin: 0.75rem 0;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }

    .feature-card:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }

    .feature-card h4 {
        color: white;
        font-size: 16px;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
    }

    .feature-card p {
        color: var(--gray-light);
        font-size: 13px;
        margin: 0;
        line-height: 1.4;
    }

    /* Enhanced Table Styling */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid var(--dark-border);
        background: var(--dark-card);
    }

    /* Enhanced Metrics Display */
    .stMetric {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(45, 55, 72, 0.8));
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid var(--dark-border);
        backdrop-filter: blur(10px);
    }

    .stMetric label {
        color: var(--gray-light) !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }

    .stMetric div {
        color: white !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }

    /* Success/Error/Warning Messages */
    .stAlert {
        border-radius: 10px;
        border: 1px solid;
        font-size: 14px;
        background: transparent !important;
    }

    .stAlert.stSuccess {
        background: rgba(16, 185, 129, 0.1) !important;
        border-color: var(--success) !important;
    }

    .stAlert.stError {
        background: rgba(239, 68, 68, 0.1) !important;
        border-color: var(--danger) !important;
    }

    .stAlert.stWarning {
        background: rgba(245, 158, 11, 0.1) !important;
        border-color: var(--warning) !important;
    }

    .stAlert.stInfo {
        background: rgba(59, 130, 246, 0.1) !important;
        border-color: var(--info) !important;
    }

    /* Enhanced Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #1e293b, #2d3748);
        border: 1px solid var(--dark-border);
        border-radius: 8px;
        font-weight: 500;
        color: white;
        transition: all 0.3s ease;
    }

    .streamlit-expanderHeader:hover {
        border-color: var(--orange-primary);
    }

    .streamlit-expanderContent {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid var(--dark-border);
        border-top: none;
        border-radius: 0 0 8px 8px;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }

    ::-webkit-scrollbar-track {
        background: #1e293b;
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb {
        background: var(--orange-primary);
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--orange-secondary);
    }

    /* Code blocks */
    .stCodeBlock {
        background: #1e293b;
        border-radius: 8px;
        border: 1px solid var(--dark-border);
    }

    /* Logo Styling */
    .logo {
        text-align: center;
        margin-bottom: 1.5rem;
    }

    .logo-text {
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--orange-primary), var(--orange-light));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.5px;
    }

    /* Spacing Improvements */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .stColumn {
        padding: 0.5rem;
    }

    /* Badge Styling */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        font-size: 11px;
        font-weight: 600;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .badge-success {
        background: rgba(16, 185, 129, 0.2);
        color: var(--success);
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .badge-danger {
        background: rgba(239, 68, 68, 0.2);
        color: var(--danger);
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    .badge-warning {
        background: rgba(245, 158, 11, 0.2);
        color: var(--warning);
        border: 1px solid rgba(245, 158, 11, 0.3);
    }

    .badge-info {
        background: rgba(59, 130, 246, 0.2);
        color: var(--info);
        border: 1px solid rgba(59, 130, 246, 0.3);
    }

    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--dark-border), transparent);
        margin: 1.5rem 0;
    }

    /* Loading Spinner */
    .stSpinner > div {
        border-color: var(--orange-primary) transparent transparent transparent !important;
    }

    /* Database Table Header */
    .dataframe-header {
        background: linear-gradient(135deg, var(--orange-primary), var(--orange-secondary));
        color: white;
        font-weight: 600;
        padding: 0.75rem;
    }

    /* Record Count Badge */
    .record-count {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background: rgba(249, 115, 22, 0.1);
        border: 1px solid rgba(249, 115, 22, 0.3);
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        color: var(--orange-light);
        margin-bottom: 1rem;
    }

    /* Status Indicator */
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 0.5rem;
    }

    .status-active {
        background: var(--success);
        box-shadow: 0 0 8px var(--success);
    }

    .status-inactive {
        background: var(--danger);
        box-shadow: 0 0 8px var(--danger);
    }

    /* Data Card */
    .data-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(45, 55, 72, 0.9));
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid var(--dark-border);
        margin-bottom: 1rem;
        backdrop-filter: blur(10px);
    }

    .data-card h3 {
        color: white;
        font-size: 1.1rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--dark-border);
    }

    /* Tooltip Styling */
    [data-testid="stTooltip"] {
        background: var(--dark-card) !important;
        border: 1px solid var(--dark-border) !important;
        border-radius: 8px !important;
        color: white !important;
    }

    /* Animation for important elements */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }

    /* Glowing effect for important buttons */
    .glow-button {
        box-shadow: 0 0 15px rgba(249, 115, 22, 0.5);
    }

    /* Highlighted text */
    .highlight {
        background: linear-gradient(120deg, rgba(249, 115, 22, 0.3), transparent);
        padding: 0.1rem 0.5rem;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.user_id = ""

if 'data' not in st.session_state:
    st.session_state.data = {}
if 'logreg_model' not in st.session_state:
    st.session_state.logreg_model = None
if 'model_metrics' not in st.session_state:
    st.session_state.model_metrics = {}

# Database Manager Class
class DatabaseManager:
    def __init__(self):
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**DATABASE_CONFIG)
            return self.connection
        except Error as e:
            st.error(f"❌ Database connection error: {str(e)}")
            return None
    
    def execute_query(self, query, params=None, fetch=True):
        """Execute SQL query"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
                cursor.close()
                return result
            else:
                self.connection.commit()
                affected_rows = cursor.rowcount
                cursor.close()
                return affected_rows
                
        except Error as e:
            st.error(f"❌ Query execution error: {str(e)}")
            return None
    
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()

# Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# User Authentication Functions
def check_database_tables():
    """Check if database tables exist"""
    db = DatabaseManager()
    if db.connect():
        try:
            cursor = db.connection.cursor()
            cursor.execute("SHOW TABLES LIKE 'users'")
            users_exists = cursor.fetchone() is not None
            
            cursor.execute("SHOW TABLES LIKE 'customers'")
            customers_exists = cursor.fetchone() is not None
            
            cursor.close()
            db.close()
            
            if not users_exists or not customers_exists:
                st.error("❌ Database tables not found. Please run the SQL script to create tables.")
                return False
            return True
            
        except:
            db.close()
            return False
    return False

def initialize_default_users():
    """Create default users if they don't exist"""
    db = DatabaseManager()
    if db.connect():
        try:
            query = "SELECT COUNT(*) as count FROM users"
            result = db.execute_query(query)
            
            if result and result[0]['count'] == 0:
                admin_password = hash_password("admin123")
                db.execute_query(
                    "INSERT INTO users (username, password) VALUES (%s, %s)",
                    ('admin', admin_password),
                    fetch=False
                )
                
                user_password = hash_password("user123")
                db.execute_query(
                    "INSERT INTO users (username, password) VALUES (%s, %s)",
                    ('user', user_password),
                    fetch=False
                )
                
                st.success("✅ Default users created: admin/admin123, user/user123")
            
            db.close()
            return True
            
        except Exception as e:
            st.error(f"Error initializing users: {str(e)}")
            db.close()
            return False
    return False

def authenticate_user(username, password):
    """Authenticate user"""
    db = DatabaseManager()
    if db.connect():
        hashed_password = hash_password(password)
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        user = db.execute_query(query, (username, hashed_password))
        
        db.close()
        
        if user:
            return user[0]
    return None

def register_user(username, password):
    """Register new user"""
    db = DatabaseManager()
    if db.connect():
        check_query = "SELECT * FROM users WHERE username = %s"
        existing_user = db.execute_query(check_query, (username,))
        
        if existing_user:
            db.close()
            return False, "Username already exists"
        
        hashed_password = hash_password(password)
        insert_query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        result = db.execute_query(insert_query, (username, hashed_password), fetch=False)
        
        db.close()
        
        if result:
            return True, "Registration successful!"
        else:
            return False, "Registration failed"
    
    return False, "Database connection failed"

def save_prediction_to_db(customer_data, prediction, probability, username):
    """Save prediction to database"""
    db = DatabaseManager()
    if db.connect():
        try:
            if probability >= 0.7:
                recommendation = "عرض استبقاء فوري: 30% خصم لمدة 3 أشهر"
            elif probability >= 0.5:
                recommendation = "عرض استبقاء: 20% خصم لمدة شهرين"
            elif probability >= 0.3:
                recommendation = "عرض ترويجي: 10% خصم لمدة شهر"
            else:
                recommendation = "عرض ولاء: برنامج نقاط"
            
            query = """
            INSERT INTO customers (
                tenure, monthly_charges, total_charges, senior_citizen, partner,
                dependents, phone_service, multiple_lines, internet_service,
                online_security, online_backup, device_protection, tech_support,
                streaming_tv, streaming_movies, contract, payment_method, gender,
                churn_prob, recommended_offer
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                customer_data.get('tenure', 0),
                customer_data.get('monthly_charges', 0),
                customer_data.get('total_charges', 0),
                customer_data.get('senior_citizen', 0),
                customer_data.get('partner', 0),
                customer_data.get('dependents', 0),
                customer_data.get('phone_service', 0),
                customer_data.get('multiple_lines', ''),
                customer_data.get('internet_service', ''),
                customer_data.get('online_security', ''),
                customer_data.get('online_backup', ''),
                customer_data.get('device_protection', ''),
                customer_data.get('tech_support', ''),
                customer_data.get('streaming_tv', ''),
                customer_data.get('streaming_movies', ''),
                customer_data.get('contract', ''),
                customer_data.get('payment_method', ''),
                customer_data.get('gender', ''),
                float(probability),
                recommendation
            )
            
            result = db.execute_query(query, values, fetch=False)
            db.close()
            
            return result is not None
            
        except Exception as e:
            st.error(f"❌ Error saving to database: {str(e)}")
            db.close()
            return False
    return False

def get_database_stats():
    """Get statistics from database"""
    db = DatabaseManager()
    if db.connect():
        stats = {}
        
        try:
            query1 = "SELECT COUNT(*) as total FROM customers"
            result1 = db.execute_query(query1)
            stats['total_customers'] = result1[0]['total'] if result1 else 0
            
            query2 = "SELECT COUNT(*) as high_risk FROM customers WHERE churn_prob > 0.5"
            result2 = db.execute_query(query2)
            stats['high_risk'] = result2[0]['high_risk'] if result2 else 0
            
            query3 = "SELECT AVG(churn_prob) as avg_prob FROM customers WHERE churn_prob IS NOT NULL"
            result3 = db.execute_query(query3)
            stats['avg_prob'] = float(result3[0]['avg_prob']) if result3 and result3[0]['avg_prob'] else 0.0
            
            db.close()
            return stats
            
        except:
            db.close()
            return {}
    return {}

# Enhanced Login Page
def show_login_page():
    """Display enhanced login/registration page"""
    
    if not check_database_tables():
        st.error("❌ Database tables not found. Please create them first.")
        return
    
    initialize_default_users()
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    st.markdown('<div class="logo">', unsafe_allow_html=True)
    st.markdown('<h1 class="logo-text">📱 Orange Telecom</h1>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<p class="login-subtitle">AI-Powered Customer Churn Prediction System<br>Predict and prevent customer churn with machine learning</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 **Login**", "📝 **Register**"])
    
    with tab1:
        st.markdown('<h3 style="color: white; margin-bottom: 1.5rem; font-size: 1.2rem;">Login to Your Account</h3>', unsafe_allow_html=True)
        
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button("**Login**", type="primary", use_container_width=True):
                if username and password:
                    with st.spinner("Authenticating..."):
                        user = authenticate_user(username, password)
                        if user:
                            st.session_state.authenticated = True
                            st.session_state.username = user['username']
                            st.session_state.user_id = user['id']
                            st.success(f"Welcome back, {username}!")
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
                else:
                    st.warning("Please enter username and password")
        
        st.markdown("---")
        with st.expander("📋 **Demo Credentials**"):
            st.markdown("""
            **Admin Account:**
            - Username: `admin`
            - Password: `admin123`
            
            **User Account:**
            - Username: `user`
            - Password: `user123`
            
            *Use these credentials to test the application*
            """)
    
    with tab2:
        st.markdown('<h3 style="color: white; margin-bottom: 1.5rem; font-size: 1.2rem;">Create New Account</h3>', unsafe_allow_html=True)
        
        new_username = st.text_input("Choose Username", placeholder="Enter new username")
        new_password = st.text_input("Choose Password", type="password", placeholder="Minimum 6 characters")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        if st.button("**Register Account**", type="primary", use_container_width=True):
            if not all([new_username, new_password, confirm_password]):
                st.warning("Please fill all fields")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                with st.spinner("Creating account..."):
                    success, message = register_user(new_username, new_password)
                    if success:
                        st.success(message)
                        st.info("You can now login with your credentials")
                    else:
                        st.error(message)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Load and preprocess data function
@st.cache_data
def load_and_preprocess_data():
    try:
        app_dir = os.path.dirname(__file__)
        file_path = os.path.join(app_dir, "Customer-Churn.csv")
        df = pd.read_csv(file_path, delimiter="\t")
        
        df['TotalCharges'] = df['TotalCharges'].astype(str).str.strip()
        df['TotalCharges'] = df['TotalCharges'].replace('', np.nan)
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
        df['TotalCharges'].fillna(df['TotalCharges'].median(), inplace=True)
        
        st.session_state.data['original'] = df.copy()
        
        df_processed = df.copy()
        df_processed.drop(['customerID'], axis=1, inplace=True)
        
        binary_cols = ['Partner', 'Dependents', 'PhoneService', 'PaperlessBilling', 'Churn']
        for col in binary_cols:
            df_processed[col] = df_processed[col].map({'Yes': 1, 'No': 0})
        
        categorical_cols = ['MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup', 
                          'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies', 
                          'Contract', 'PaymentMethod', 'gender']
        df_processed = pd.get_dummies(df_processed, columns=categorical_cols, drop_first=True)
        
        num_cols = ['tenure', 'MonthlyCharges', 'TotalCharges']
        scaler = StandardScaler()
        df_processed[num_cols] = scaler.fit_transform(df_processed[num_cols])
        
        st.session_state.data['processed'] = df_processed
        
        X = df_processed.drop('Churn', axis=1)
        y = df_processed['Churn']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        return df, df_processed, X_train, X_test, y_train, y_test, scaler
        
    except FileNotFoundError:
        st.error("❌ Customer-Churn.csv file not found. Please ensure the dataset is in the same directory.")
        return None
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return None

# Train Logistic Regression model
def train_logistic_regression(X_train, y_train, X_test, y_test, C=1.0):
    try:
        logreg = LogisticRegression(
            max_iter=1000, 
            class_weight='balanced', 
            random_state=42,
            C=C
        )
        logreg.fit(X_train, y_train)
        
        y_pred = logreg.predict(X_test)
        y_prob = logreg.predict_proba(X_test)[:, 1]
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_prob),
            'model': logreg,
            'predictions': y_pred,
            'probabilities': y_prob
        }
        
        return metrics
    except Exception as e:
        st.error(f"❌ Error training model: {str(e)}")
        return None

# Enhanced plotting functions
def plot_confusion_matrix(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(8, 6))
    
    sns.heatmap(cm, annot=True, fmt='d', cmap='Oranges', 
                xticklabels=['No Churn', 'Churn'],
                yticklabels=['No Churn', 'Churn'],
                ax=ax, annot_kws={"size": 12, "color": "white"})
    
    ax.set_xlabel('Predicted Label', fontsize=12, fontweight=600, color='white')
    ax.set_ylabel('True Label', fontsize=12, fontweight=600, color='white')
    ax.set_title('Confusion Matrix', fontsize=14, fontweight=700, color='#f97316', pad=20)
    
    ax.tick_params(colors='white', labelsize=10)
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#1e293b')
    
    plt.tight_layout()
    return fig

def plot_feature_importance(model, feature_names, top_n=15):
    importance = abs(model.coef_[0])
    indices = np.argsort(importance)[-top_n:]
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#1e293b')
    
    colors = plt.cm.Oranges(np.linspace(0.3, 1, len(indices)))
    bars = ax.barh(range(len(indices)), importance[indices], color=colors, height=0.6)
    
    ax.set_yticks(range(len(indices)))
    ax.set_yticklabels([feature_names[i] for i in indices], color='white', fontsize=10)
    ax.set_xlabel('Feature Importance (Absolute Coefficient)', 
                 fontsize=12, fontweight=600, color='white', labelpad=10)
    ax.set_title(f'Top {top_n} Most Important Features', 
                fontsize=14, fontweight=700, color='#f97316', pad=20)
    
    ax.grid(True, alpha=0.2, axis='x', color='#475569', linestyle='--')
    
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width + 0.001, bar.get_y() + bar.get_height()/2,
                f'{width:.3f}', ha='left', va='center', 
                fontsize=9, fontweight=600, color='white')
    
    plt.tight_layout()
    return fig

# Enhanced Main App
def show_main_app():
    """Main application after login"""
    
    # Enhanced Sidebar
    st.sidebar.markdown(f"""
    <div class="user-info fade-in">
        <h4>👤 {st.session_state.username}</h4>
        <p>User ID: {st.session_state.user_id}</p>
    </div>
    """, unsafe_allow_html=True)
    
    menu_items = ["🏠 **Dashboard**", "📊 **Data Analysis**", "🤖 **Model Training**", 
                  "🔮 **New Prediction**", "📋 **Database**", "⚙️ **Settings**"]
    
    if st.session_state.username == 'admin':
        menu_items.append("👨‍💼 **User Management**")
    
    choice = st.sidebar.selectbox("**Navigation**", menu_items)
    
    if st.sidebar.button("🚪 **Logout**", type="primary", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.user_id = ""
        st.rerun()
    
    # Main Content
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">Orange Telecom - Churn Prediction System</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #94a3b8; margin-bottom: 2rem;">Predict customer churn and optimize retention strategies using machine learning</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Database Page - FIXED AND ENHANCED
    if choice == "📋 **Database**":
        st.markdown('<h2 class="section-header">📋 Database Management</h2>', unsafe_allow_html=True)
        st.markdown('<p style="color: #94a3b8; margin-bottom: 1.5rem;">View and manage customer prediction records stored in the database.</p>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["👥 **Customer Records**", "📊 **Statistics**"])
        
        with tab1:
            st.markdown('<div class="data-card fade-in">', unsafe_allow_html=True)
            st.markdown('<h3>Customer Prediction Records</h3>', unsafe_allow_html=True)
            
            db = DatabaseManager()
            if db.connect():
                # First, get column names to check if created_at exists
                cursor = db.connection.cursor()
                cursor.execute("SHOW COLUMNS FROM customers")
                columns = [column[0] for column in cursor.fetchall()]
                cursor.close()
                
                # Build the query based on available columns
                if 'created_at' in columns:
                    query = "SELECT id, tenure, monthly_charges, total_charges, churn_prob, recommended_offer, created_at FROM customers ORDER BY id DESC LIMIT 100"
                else:
                    query = "SELECT id, tenure, monthly_charges, total_charges, churn_prob, recommended_offer FROM customers ORDER BY id DESC LIMIT 100"
                
                customers = db.execute_query(query)
                db.close()
                
                if customers:
                    df_customers = pd.DataFrame(customers)
                    
                    # Format the date column if it exists
                    if 'created_at' in df_customers.columns:
                        df_customers['created_at'] = pd.to_datetime(df_customers['created_at']).dt.strftime('%Y-%m-%d %H:%M')
                    
                    # Display record count badge
                    st.markdown(f'<div class="record-count">📊 Showing {min(len(df_customers), 20)} of {len(df_customers)} records</div>', unsafe_allow_html=True)
                    
                    # Enhanced dataframe display
                    st.dataframe(
                        df_customers.head(20),
                        use_container_width=True,
                        column_config={
                            "id": "ID",
                            "tenure": "Tenure (months)",
                            "monthly_charges": st.column_config.NumberColumn("Monthly Charges", format="$%.2f"),
                            "total_charges": st.column_config.NumberColumn("Total Charges", format="$%.2f"),
                            "churn_prob": st.column_config.NumberColumn("Churn Probability", format="%.2%"),
                            "recommended_offer": "Recommended Offer",
                            "created_at": "Created Date"
                        } if 'created_at' in df_customers.columns else {
                            "id": "ID",
                            "tenure": "Tenure (months)",
                            "monthly_charges": st.column_config.NumberColumn("Monthly Charges", format="$%.2f"),
                            "total_charges": st.column_config.NumberColumn("Total Charges", format="$%.2f"),
                            "churn_prob": st.column_config.NumberColumn("Churn Probability", format="%.2%"),
                            "recommended_offer": "Recommended Offer"
                        }
                    )
                    
                    # Enhanced summary stats with cards
                    st.markdown("---")
                    st.markdown('<h3 style="color: white; margin-bottom: 1rem;">📈 Summary Statistics</h3>', unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>Total Records</h3>
                            <h1>{len(df_customers)}</h1>
                            <p>In database</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        if 'churn_prob' in df_customers.columns:
                            avg_prob = df_customers['churn_prob'].mean()
                            color = "#ef4444" if avg_prob > 0.5 else "#10b981" if avg_prob < 0.3 else "#f59e0b"
                            st.markdown(f"""
                            <div class="metric-card">
                                <h3>Avg Probability</h3>
                                <h1 style='color: {color};'>{avg_prob:.1%}</h1>
                                <p>Churn risk</p>
                            </div>
                            """, unsafe_allow_html=True)
                    with col3:
                        if 'monthly_charges' in df_customers.columns:
                            avg_charge = df_customers['monthly_charges'].mean()
                            st.markdown(f"""
                            <div class="metric-card">
                                <h3>Avg Monthly</h3>
                                <h1>${avg_charge:.2f}</h1>
                                <p>Average charges</p>
                            </div>
                            """, unsafe_allow_html=True)
                    with col4:
                        if 'churn_prob' in df_customers.columns:
                            high_risk = len(df_customers[df_customers['churn_prob'] > 0.5])
                            st.markdown(f"""
                            <div class="metric-card">
                                <h3>High Risk</h3>
                                <h1 style='color: #ef4444;'>{high_risk}</h1>
                                <p>Require action</p>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Add export functionality
                    st.markdown("---")
                    st.markdown('<h3 style="color: white; margin-bottom: 1rem;">📤 Export Data</h3>', unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📥 Export as CSV", use_container_width=True):
                            csv = df_customers.to_csv(index=False)
                            st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name="customer_predictions.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                    with col2:
                        if st.button("📊 Generate Report", use_container_width=True):
                            st.info("Report generation feature coming soon!")
                else:
                    st.info("📭 No customer records found in the database.")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="data-card fade-in">', unsafe_allow_html=True)
            st.markdown('<h3>Database Statistics</h3>', unsafe_allow_html=True)
            
            stats = get_database_stats()
            
            if stats:
                # Main Statistics Cards
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total = stats.get('total_customers', 0)
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Total Predictions</h3>
                        <h1>{total:,}</h1>
                        <p>All-time records</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    high_risk = stats.get('high_risk', 0)
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>High Risk Customers</h3>
                        <h1 style='color: #ef4444;'>{high_risk:,}</h1>
                        <p>Immediate attention needed</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    avg_prob = stats.get('avg_prob', 0)
                    if avg_prob > 0.7:
                        status = "Critical"
                        color = "#ef4444"
                    elif avg_prob > 0.5:
                        status = "High"
                        color = "#f59e0b"
                    elif avg_prob > 0.3:
                        status = "Medium"
                        color = "#3b82f6"
                    else:
                        status = "Low"
                        color = "#10b981"
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Average Risk Score</h3>
                        <h1 style='color: {color};'>{avg_prob:.1%}</h1>
                        <p>Status: {status}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Risk Distribution Visualization
                st.markdown("---")
                st.markdown('<h3 style="color: white; margin-bottom: 1rem;">📊 Risk Distribution</h3>', unsafe_allow_html=True)
                
                if stats['total_customers'] > 0:
                    low_risk = stats['total_customers'] - stats['high_risk']
                    
                    fig, ax = plt.subplots(figsize=(10, 6))
                    fig.patch.set_facecolor('#0f172a')
                    ax.set_facecolor('#1e293b')
                    
                    categories = ['Low Risk', 'High Risk']
                    values = [low_risk, high_risk]
                    colors = ['#10b981', '#ef4444']
                    
                    bars = ax.bar(categories, values, color=colors, edgecolor='white', linewidth=2)
                    
                    ax.set_ylabel('Number of Customers', color='white', fontsize=12, fontweight=600)
                    ax.set_title('Customer Risk Distribution', color='#f97316', fontsize=14, fontweight=700, pad=20)
                    ax.tick_params(colors='white', labelsize=10)
                    
                    # Add value labels on bars
                    for bar, value in zip(bars, values):
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                               f'{value:,}', ha='center', va='bottom',
                               color='white', fontweight=600, fontsize=11)
                    
                    st.pyplot(fig)
                    
                    # Risk Insights
                    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
                    st.markdown("### 🔍 Risk Insights")
                    if high_risk / stats['total_customers'] > 0.3:
                        st.markdown("⚠️ **High Alert**: Over 30% of customers are at high risk of churn. Immediate retention strategies needed.")
                    elif high_risk / stats['total_customers'] > 0.1:
                        st.markdown("📊 **Moderate Risk**: 10-30% of customers are at high risk. Proactive measures recommended.")
                    else:
                        st.markdown("✅ **Low Risk**: Less than 10% of customers are at high risk. Good customer retention.")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Database Health Check
                st.markdown("---")
                st.markdown('<h3 style="color: white; margin-bottom: 1rem;">⚡ Database Health</h3>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class="feature-card">
                        <h4>📈 Data Growth</h4>
                        <p><span class="highlight">{stats['total_customers']:,} records</span> stored</p>
                        <p><span class="highlight">{stats['high_risk']:,}</span> require attention</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    db = DatabaseManager()
                    if db.connect():
                        cursor = db.connection.cursor()
                        cursor.execute("SELECT table_name, table_rows FROM information_schema.tables WHERE table_schema = %s", (DATABASE_CONFIG['database'],))
                        tables_info = cursor.fetchall()
                        cursor.close()
                        db.close()
                        
                        table_count = len(tables_info)
                        st.markdown(f"""
                        <div class="feature-card">
                            <h4>🗃️ Database Status</h4>
                            <p><span class="status-indicator status-active"></span> Connected</p>
                            <p><span class="highlight">{table_count} tables</span> active</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("📊 No statistics available. Add some predictions first!")
            
            st.markdown('</div>', unsafe_allow_html=True)

    # Other pages remain the same...
    elif choice == "🏠 **Dashboard**":
        st.markdown('<h2 class="section-header">📊 Dashboard Overview</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"""
            <div class="feature-card fade-in">
                <h3>👋 Welcome back, {st.session_state.username}!</h3>
                <p>Last login: Successfully authenticated • System ready for analysis</p>
            </div>
            """, unsafe_allow_html=True)
        
        db_stats = get_database_stats()
        
        st.markdown('<h3 class="subsection-header">System Statistics</h3>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card fade-in">
                <h3>Total Predictions</h3>
                <h1>{db_stats.get('total_customers', 0):,}</h1>
                <p>Saved in database</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card fade-in">
                <h3>High Risk Customers</h3>
                <h1 style='color: #ef4444;'>{db_stats.get('high_risk', 0):,}</h1>
                <p>Require immediate action</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_prob = db_stats.get('avg_prob', 0)
            risk_color = '#ef4444' if avg_prob > 0.5 else '#10b981' if avg_prob < 0.3 else '#f59e0b'
            st.markdown(f"""
            <div class="metric-card fade-in">
                <h3>Average Risk Score</h3>
                <h1 style='color: {risk_color};'>{avg_prob:.1%}</h1>
                <p>Overall churn probability</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<h2 class="section-header">⚡ Quick Actions</h2>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        actions = [
            {"icon": "📊", "title": "Analyze Data", "description": "Explore customer insights and trends", "button": "Go to Analysis"},
            {"icon": "🤖", "title": "Train Model", "description": "Build and optimize prediction models", "button": "Train Model"},
            {"icon": "🔮", "title": "New Prediction", "description": "Predict churn for new customers", "button": "Make Prediction"}
        ]
        
        for idx, action in enumerate(actions):
            with [col1, col2, col3][idx]:
                st.markdown(f"""
                <div class="feature-card fade-in">
                    <h4>{action['icon']} {action['title']}</h4>
                    <p>{action['description']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(action['button'], key=f"action_{idx}", use_container_width=True):
                    pass

    # Data Analysis Page
    elif choice == "📊 **Data Analysis**":
        st.markdown('<h2 class="section-header">📊 Customer Data Analysis</h2>', unsafe_allow_html=True)
        
        if 'df' not in st.session_state.data:
            st.info("📝 **Please load data first**")
            if st.button("📥 **Load Dataset**", type="primary", use_container_width=True):
                with st.spinner("Loading and processing data..."):
                    result = load_and_preprocess_data()
                    if result:
                        df, df_processed, X_train, X_test, y_train, y_test, scaler = result
                        st.session_state.data.update({
                            'df': df,
                            'df_processed': df_processed,
                            'X_train': X_train,
                            'X_test': X_test,
                            'y_train': y_train,
                            'y_test': y_test,
                            'scaler': scaler
                        })
                        st.success("✅ Data loaded successfully!")
                        st.rerun()
        else:
            df = st.session_state.data['df']
            
            st.markdown('<h3 class="subsection-header">Dataset Overview</h3>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Customers", f"{len(df):,}")
            
            with col2:
                if 'Churn' in df.columns:
                    churned = len(df[df['Churn'] == 'Yes'])
                    st.metric("Churned Customers", f"{churned:,}")
            
            with col3:
                if 'Churn' in df.columns and len(df) > 0:
                    churn_rate = (churned / len(df)) * 100
                    st.metric("Churn Rate", f"{churn_rate:.1f}%")
            
            with col4:
                if 'MonthlyCharges' in df.columns:
                    avg_charge = df['MonthlyCharges'].mean()
                    st.metric("Avg Monthly Charge", f"${avg_charge:.2f}")
            
            with st.expander("📋 **View Data Sample**", expanded=True):
                st.markdown(f'<p style="color: #94a3b8; margin-bottom: 0.5rem;">Showing first 10 rows of {len(df):,} total records</p>', unsafe_allow_html=True)
                st.dataframe(df.head(10), use_container_width=True)
            
            st.markdown('<h2 class="section-header">📈 Visual Analysis</h2>', unsafe_allow_html=True)
            
            viz_type = st.selectbox("**Select Visualization Type**", 
                                   ["Churn Distribution", "Contract Analysis", 
                                    "Payment Method Analysis", "Tenure Analysis"])
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            plt.style.use('dark_background')
            fig.patch.set_facecolor('#0f172a')
            ax.set_facecolor('#1e293b')
            
            if viz_type == "Churn Distribution" and 'Churn' in df.columns:
                churn_counts = df['Churn'].value_counts()
                colors = ['#f97316', '#ea580c']
                ax.pie(churn_counts.values, labels=churn_counts.index, 
                       autopct='%1.1f%%', colors=colors, startangle=90,
                       textprops={'color': 'white', 'fontsize': 11})
                ax.set_title('Customer Churn Distribution', color='#f97316', fontsize=13, fontweight=600, pad=20)
                
            elif viz_type == "Contract Analysis" and 'Contract' in df.columns and 'Churn' in df.columns:
                contract_churn = df.groupby('Contract')['Churn'].apply(
                    lambda x: (x == 'Yes').mean() * 100
                ).sort_values(ascending=False)
                
                bars = ax.bar(contract_churn.index, contract_churn.values, 
                             color=['#f97316', '#ea580c', '#fdba74'][:len(contract_churn)])
                ax.set_ylabel('Churn Rate (%)', color='white', fontsize=11)
                ax.set_title('Churn Rate by Contract Type', color='#f97316', fontsize=13, fontweight=600, pad=20)
                ax.tick_params(axis='x', rotation=45, colors='white', labelsize=10)
                ax.tick_params(axis='y', colors='white', labelsize=10)
                
                for bar, value in zip(bars, contract_churn.values):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                           f'{value:.1f}%', ha='center', va='bottom', 
                           color='white', fontweight=600, fontsize=10)
                
            elif viz_type == "Payment Method Analysis" and 'PaymentMethod' in df.columns and 'Churn' in df.columns:
                payment_churn = df.groupby('PaymentMethod')['Churn'].apply(
                    lambda x: (x == 'Yes').mean() * 100
                ).sort_values(ascending=False)
                
                bars = ax.bar(range(len(payment_churn)), payment_churn.values,
                             color=plt.cm.Oranges(np.linspace(0.4, 1, len(payment_churn))))
                ax.set_ylabel('Churn Rate (%)', color='white', fontsize=11)
                ax.set_title('Churn Rate by Payment Method', color='#f97316', fontsize=13, fontweight=600, pad=20)
                ax.set_xticks(range(len(payment_churn)))
                ax.set_xticklabels(payment_churn.index, rotation=45, ha='right', color='white', fontsize=10)
                ax.tick_params(axis='y', colors='white', labelsize=10)
                
            else:
                if 'tenure' in df.columns:
                    ax.hist(df['tenure'], bins=30, color='#f97316', edgecolor='white', alpha=0.8)
                    ax.set_xlabel('Tenure (Months)', color='white', fontsize=11)
                    ax.set_ylabel('Number of Customers', color='white', fontsize=11)
                    ax.set_title('Customer Tenure Distribution', color='#f97316', fontsize=13, fontweight=600, pad=20)
                    ax.tick_params(colors='white', labelsize=10)
            
            st.pyplot(fig)

    # Model Training Page
    elif choice == "🤖 **Model Training**":
        st.markdown('<h2 class="section-header">🤖 Model Training</h2>', unsafe_allow_html=True)
        
        if 'X_train' not in st.session_state.data:
            st.warning("⚠️ **Please load the data from Data Analysis page first.**")
            st.info("Navigate to 📊 **Data Analysis** and click 'Load Dataset' to begin.")
        else:
            X_train = st.session_state.data['X_train']
            X_test = st.session_state.data['X_test']
            y_train = st.session_state.data['y_train']
            y_test = st.session_state.data['y_test']
            
            st.sidebar.markdown('<h3 style="color: white; margin-bottom: 1rem;">⚙️ Model Parameters</h3>', unsafe_allow_html=True)
            C_value = st.sidebar.slider("**Regularization Strength (C)**", 0.01, 10.0, 1.0, 0.1,
                                       help="Smaller values specify stronger regularization")
            
            if st.button("🚀 **Train Logistic Regression Model**", type="primary", use_container_width=True):
                with st.spinner("Training model... This may take a moment."):
                    metrics = train_logistic_regression(
                        X_train, y_train, X_test, y_test, 
                        C=C_value
                    )
                    
                    if metrics:
                        st.session_state.logreg_model = metrics['model']
                        st.session_state.model_metrics = metrics
                        
                        st.success("✅ Model trained successfully!")
                        
                        st.markdown('<h2 class="section-header">📊 Model Performance Metrics</h2>', unsafe_allow_html=True)
                        
                        col1, col2, col3, col4, col5 = st.columns(5)
                        metric_configs = [
                            ("Accuracy", metrics['accuracy'], "#f97316"),
                            ("Precision", metrics['precision'], "#10b981"),
                            ("Recall", metrics['recall'], "#3b82f6"),
                            ("F1-Score", metrics['f1_score'], "#8b5cf6"),
                            ("ROC AUC", metrics['roc_auc'], "#f59e0b")
                        ]
                        
                        for idx, (name, value, color) in enumerate(metric_configs):
                            with [col1, col2, col3, col4, col5][idx]:
                                st.markdown(f"""
                                <div class="metric-card">
                                    <h3>{name}</h3>
                                    <h1 style='color: {color};'>{value:.3f}</h1>
                                    <p>{'Higher is better' if name != 'Loss' else 'Lower is better'}</p>
                                </div>
                                """, unsafe_allow_html=True)
            
            if st.session_state.model_metrics:
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<h3 style="color: white; margin-bottom: 1rem;">Confusion Matrix</h3>', unsafe_allow_html=True)
                    fig_cm = plot_confusion_matrix(y_test, st.session_state.model_metrics['predictions'])
                    st.pyplot(fig_cm)
                
                with col2:
                    st.markdown('<h3 style="color: white; margin-bottom: 1rem;">Feature Importance</h3>', unsafe_allow_html=True)
                    fig_fi = plot_feature_importance(
                        st.session_state.logreg_model,
                        X_train.columns,
                        top_n=12
                    )
                    st.pyplot(fig_fi)
                
                st.markdown('<h3 style="color: white; margin: 2rem 0 1rem 0;">📋 Detailed Classification Report</h3>', unsafe_allow_html=True)
                report = classification_report(y_test, st.session_state.model_metrics['predictions'])
                st.code(report, language='text')

    # Prediction Page
    elif choice == "🔮 **New Prediction**":
        st.markdown('<h2 class="section-header">🔮 Customer Churn Prediction</h2>', unsafe_allow_html=True)
        st.markdown('<p style="color: #94a3b8; margin-bottom: 1.5rem;">Enter customer details to predict churn probability and get retention recommendations.</p>', unsafe_allow_html=True)
        
        if not st.session_state.logreg_model:
            st.warning("⚠️ **Please train the model first from the Model Training page.**")
            st.info("You can still make predictions using basic calculations.")
            use_basic = True
        else:
            use_basic = False
            model = st.session_state.logreg_model
            scaler = st.session_state.data['scaler']
            X_train = st.session_state.data['X_train']
        
        with st.form("prediction_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<h3 class="subsection-header">📊 Customer Information</h3>', unsafe_allow_html=True)
                tenure = st.slider("Tenure (months)", 0, 72, 12, 
                                 help="Number of months the customer has been with the company")
                monthly_charges = st.number_input("Monthly Charges ($)", 0.0, 200.0, 64.76, 0.01,
                                                help="Monthly service charges")
                total_charges = st.number_input("Total Charges ($)", 0.0, 10000.0, 2283.3, 0.01,
                                              help="Total amount charged to customer")
                senior_citizen = st.selectbox("Senior Citizen", [0, 1], 
                                            format_func=lambda x: "No" if x == 0 else "Yes")
                partner = st.selectbox("Partner", [0, 1], 
                                     format_func=lambda x: "No" if x == 0 else "Yes")
                dependents = st.selectbox("Dependents", [0, 1], 
                                        format_func=lambda x: "No" if x == 0 else "Yes")
            
            with col2:
                st.markdown('<h3 class="subsection-header">📱 Service Details</h3>', unsafe_allow_html=True)
                contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"],
                                      help="Contract type")
                payment_method = st.selectbox("Payment Method", 
                                            ["Electronic check", "Mailed check", 
                                             "Bank transfer (automatic)", "Credit card (automatic)"])
                internet_service = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
                phone_service = st.selectbox("Phone Service", [0, 1], 
                                           format_func=lambda x: "No" if x == 0 else "Yes")
                multiple_lines = st.selectbox("Multiple Lines", ["No", "Yes", "No phone service"])
                gender = st.selectbox("Gender", ["Female", "Male"])
            
            with st.expander("🛠️ **Additional Services**"):
                col3, col4 = st.columns(2)
                with col3:
                    online_security = st.selectbox("Online Security", ["No", "Yes", "No internet service"], index=0)
                    online_backup = st.selectbox("Online Backup", ["No", "Yes", "No internet service"], index=0)
                    device_protection = st.selectbox("Device Protection", ["No", "Yes", "No internet service"], index=0)
                with col4:
                    tech_support = st.selectbox("Tech Support", ["No", "Yes", "No internet service"], index=0)
                    streaming_tv = st.selectbox("Streaming TV", ["No", "Yes", "No internet service"], index=0)
                    streaming_movies = st.selectbox("Streaming Movies", ["No", "Yes", "No internet service"], index=0)
            
            submitted = st.form_submit_button("🔍 **Predict Churn**", type="primary", use_container_width=True)
            
            if submitted:
                customer_data = {
                    'tenure': tenure,
                    'monthly_charges': monthly_charges,
                    'total_charges': total_charges,
                    'senior_citizen': senior_citizen,
                    'partner': partner,
                    'dependents': dependents,
                    'phone_service': phone_service,
                    'multiple_lines': multiple_lines,
                    'internet_service': internet_service,
                    'online_security': online_security,
                    'online_backup': online_backup,
                    'device_protection': device_protection,
                    'tech_support': tech_support,
                    'streaming_tv': streaming_tv,
                    'streaming_movies': streaming_movies,
                    'contract': contract,
                    'payment_method': payment_method,
                    'gender': gender
                }
                
                if use_basic:
                    base_prob = 0.3
                    if contract == "Month-to-month":
                        base_prob += 0.2
                    if payment_method == "Electronic check":
                        base_prob += 0.1
                    if tenure < 6:
                        base_prob += 0.15
                    if internet_service == "Fiber optic":
                        base_prob += 0.1
                    
                    probability = min(base_prob, 0.95)
                    prediction = 1 if probability > 0.5 else 0
                    
                    st.info("ℹ️ **Using basic calculation (model not trained)**")
                else:
                    try:
                        input_data = {
                            'SeniorCitizen': senior_citizen,
                            'Partner': partner,
                            'Dependents': dependents,
                            'tenure': tenure,
                            'PhoneService': phone_service,
                            'PaperlessBilling': 1,
                            'MonthlyCharges': monthly_charges,
                            'TotalCharges': total_charges,
                            'MultipleLines_No phone service': 1 if multiple_lines == "No phone service" else 0,
                            'MultipleLines_Yes': 1 if multiple_lines == "Yes" else 0,
                            'InternetService_Fiber optic': 1 if internet_service == "Fiber optic" else 0,
                            'InternetService_No': 1 if internet_service == "No" else 0,
                            'OnlineSecurity_No internet service': 1 if online_security == "No internet service" else 0,
                            'OnlineSecurity_Yes': 1 if online_security == "Yes" else 0,
                            'OnlineBackup_No internet service': 1 if online_backup == "No internet service" else 0,
                            'OnlineBackup_Yes': 1 if online_backup == "Yes" else 0,
                            'DeviceProtection_No internet service': 1 if device_protection == "No internet service" else 0,
                            'DeviceProtection_Yes': 1 if device_protection == "Yes" else 0,
                            'TechSupport_No internet service': 1 if tech_support == "No internet service" else 0,
                            'TechSupport_Yes': 1 if tech_support == "Yes" else 0,
                            'StreamingTV_No internet service': 1 if streaming_tv == "No internet service" else 0,
                            'StreamingTV_Yes': 1 if streaming_tv == "Yes" else 0,
                            'StreamingMovies_No internet service': 1 if streaming_movies == "No internet service" else 0,
                            'StreamingMovies_Yes': 1 if streaming_movies == "Yes" else 0,
                            'Contract_One year': 1 if contract == "One year" else 0,
                            'Contract_Two year': 1 if contract == "Two year" else 0,
                            'PaymentMethod_Credit card (automatic)': 1 if payment_method == "Credit card (automatic)" else 0,
                            'PaymentMethod_Electronic check': 1 if payment_method == "Electronic check" else 0,
                            'PaymentMethod_Mailed check': 1 if payment_method == "Mailed check" else 0,
                            'gender_Male': 1 if gender == "Male" else 0
                        }
                        
                        input_df = pd.DataFrame([input_data])
                        num_cols = ['tenure', 'MonthlyCharges', 'TotalCharges']
                        input_df[num_cols] = scaler.transform(input_df[num_cols])
                        input_df = input_df.reindex(columns=X_train.columns, fill_value=0)
                        
                        prediction = model.predict(input_df)[0]
                        probability = model.predict_proba(input_df)[0][1]
                        
                        st.info("ℹ️ **Using trained model prediction**")
                        
                    except Exception as e:
                        st.error(f"❌ Model prediction error: {str(e)}")
                        probability = 0.5
                        prediction = 0
                
                save_success = save_prediction_to_db(
                    customer_data, prediction, probability, st.session_state.username
                )
                
                st.markdown("---")
                st.markdown('<h2 class="section-header">🎯 Prediction Results</h2>', unsafe_allow_html=True)
                
                if save_success:
                    st.success("✅ **Prediction saved to database**")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("**Churn Probability**", f"{probability:.1%}")
                
                with col2:
                    risk_level = "HIGH RISK" if prediction == 1 else "LOW RISK"
                    st.metric("**Risk Level**", risk_level)
                
                with col3:
                    recommendation = "Immediate Action Required" if prediction == 1 else "Monitor Regularly"
                    st.metric("**Recommendation**", recommendation)
                
                if prediction == 1:
                    st.markdown('<div class="prediction-high">', unsafe_allow_html=True)
                    st.markdown('<h3 style="color: #ef4444; margin-bottom: 1rem;">⚠️ HIGH CHURN RISK DETECTED</h3>', unsafe_allow_html=True)
                    st.markdown('<p style="color: #fca5a5; margin-bottom: 1rem;">This customer has a high probability of leaving. Immediate retention action is recommended.</p>', unsafe_allow_html=True)
                    st.markdown("**🎯 Recommended Actions:**")
                    st.markdown("1. **Immediate Retention Call** - Contact within 24 hours")
                    st.markdown("2. **Special Offer** - 30% discount for 3 months")
                    st.markdown("3. **Service Review** - Free technical support session")
                    st.markdown("4. **Contract Upgrade** - Offer annual contract benefits")
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown('<div class="prediction-low">', unsafe_allow_html=True)
                    st.markdown('<h3 style="color: #10b981; margin-bottom: 1rem;">✅ LOW CHURN RISK</h3>', unsafe_allow_html=True)
                    st.markdown('<p style="color: #a7f3d0; margin-bottom: 1rem;">This customer is likely to stay. Focus on maintenance and upselling opportunities.</p>', unsafe_allow_html=True)
                    st.markdown("**🎯 Maintenance Actions:**")
                    st.markdown("1. **Regular Check-ins** - Monthly satisfaction surveys")
                    st.markdown("2. **Upsell Opportunities** - Premium service offers")
                    st.markdown("3. **Loyalty Program** - Exclusive benefits for long-term customers")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                fig, ax = plt.subplots(figsize=(10, 2))
                
                fig.patch.set_facecolor('#0f172a')
                ax.set_facecolor('#1e293b')
                
                gradient = np.linspace(0, 1, 100).reshape(1, -1)
                ax.imshow(gradient, aspect='auto', cmap='Oranges', extent=[0, 100, 0, 1])
                
                marker_pos = probability * 100
                ax.plot(marker_pos, 0.5, 'ko', markersize=12, markerfacecolor='white', markeredgewidth=2)
                
                ax.text(marker_pos, 1.5, f'{probability:.1%}', ha='center', 
                       color='white', fontweight=700, fontsize=13, 
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='#1e293b', edgecolor='#f97316', alpha=0.9))
                
                ax.text(0, -0.5, 'Low Risk', ha='left', color='#10b981', fontsize=11, fontweight=600)
                ax.text(100, -0.5, 'High Risk', ha='right', color='#ef4444', fontsize=11, fontweight=600)
                ax.text(50, -0.5, 'Threshold', ha='center', color='#fdba74', fontsize=10, fontweight=500)
                
                ax.set_xlim(0, 100)
                ax.set_ylim(-1, 2)
                ax.set_yticks([])
                ax.set_xlabel('Churn Risk Scale', color='white', fontsize=11, fontweight=600, labelpad=10)
                ax.axvline(x=50, color='white', linestyle='--', alpha=0.5, linewidth=1)
                ax.tick_params(colors='white', labelsize=10)
                
                st.pyplot(fig)

    # Settings Page
    elif choice == "⚙️ **Settings**":
        st.markdown('<h2 class="section-header">⚙️ Settings</h2>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["👤 **Account Settings**", "🔧 **System Settings**"])
        
        with tab1:
            st.markdown('<h3 class="subsection-header">Account Information</h3>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<h3>Username</h3>', unsafe_allow_html=True)
                st.markdown(f'<h1>{st.session_state.username}</h1>', unsafe_allow_html=True)
                st.markdown('<p>Your login identifier</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<h3>User ID</h3>', unsafe_allow_html=True)
                st.markdown(f'<h1>{st.session_state.user_id}</h1>', unsafe_allow_html=True)
                st.markdown('<p>Unique identifier</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<hr>', unsafe_allow_html=True)
            st.markdown('<h3 class="subsection-header">Change Password</h3>', unsafe_allow_html=True)
            
            current_pass = st.text_input("Current Password", type="password", placeholder="Enter current password")
            new_pass = st.text_input("New Password", type="password", placeholder="Minimum 6 characters")
            confirm_pass = st.text_input("Confirm New Password", type="password", placeholder="Re-enter new password")
            
            if st.button("**Update Password**", type="primary", use_container_width=True):
                if not all([current_pass, new_pass, confirm_pass]):
                    st.warning("Please fill all fields")
                elif new_pass != confirm_pass:
                    st.error("New passwords do not match")
                elif len(new_pass) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    user = authenticate_user(st.session_state.username, current_pass)
                    if user:
                        db = DatabaseManager()
                        if db.connect():
                            hashed_password = hash_password(new_pass)
                            query = "UPDATE users SET password = %s WHERE id = %s"
                            result = db.execute_query(query, (hashed_password, st.session_state.user_id), fetch=False)
                            db.close()
                            
                            if result:
                                st.success("✅ **Password updated successfully**")
                            else:
                                st.error("❌ **Failed to update password**")
                    else:
                        st.error("❌ **Current password is incorrect**")
        
        with tab2:
            st.markdown('<h3 class="subsection-header">System Information</h3>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="feature-card">
                    <h4>📊 Database Status</h4>
                    <p>✅ Connected</p>
                    <p>Tables: users, customers</p>
                    <p>Version: 2.0</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                model_status = "✅ Trained" if st.session_state.logreg_model else "⚠️ Not Trained"
                st.markdown(f"""
                <div class="feature-card">
                    <h4>🤖 Model Status</h4>
                    <p>{model_status}</p>
                    <p>Last Updated: System Ready</p>
                    <p>Algorithm: Logistic Regression</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('<hr>', unsafe_allow_html=True)
            st.markdown('<h3 class="subsection-header">Database Connection Test</h3>', unsafe_allow_html=True)
            
            if st.button("**Test Database Connection**", type="primary", use_container_width=True):
                with st.spinner("Testing connection..."):
                    db = DatabaseManager()
                    if db.connect():
                        st.success("✅ **Database connection successful**")
                        db.close()
                    else:
                        st.error("❌ **Database connection failed**")

    # User Management Page
    elif choice == "👨‍💼 **User Management**" and st.session_state.username == 'admin':
        st.markdown('<h2 class="section-header">👨‍💼 User Management</h2>', unsafe_allow_html=True)
        st.markdown('<p style="color: #94a3b8; margin-bottom: 1.5rem;">Manage user accounts and permissions.</p>', unsafe_allow_html=True)
        
        db = DatabaseManager()
        if db.connect():
            users = db.execute_query("SELECT id, username, created_at FROM users ORDER BY id")
            
            if users:
                st.markdown('<h3 class="subsection-header">Registered Users</h3>', unsafe_allow_html=True)
                
                df_users = pd.DataFrame(users)
                df_users['created_at'] = pd.to_datetime(df_users['created_at']).dt.strftime('%Y-%m-%d %H:%M')
                
                st.dataframe(df_users, use_container_width=True)
                
                st.markdown('<hr>', unsafe_allow_html=True)
                st.markdown('<h3 class="subsection-header">Add New User</h3>', unsafe_allow_html=True)
                
                new_user = st.text_input("Username", placeholder="Enter new username")
                new_pass = st.text_input("Password", type="password", placeholder="Enter password")
                
                if st.button("**Add User**", type="primary", use_container_width=True):
                    if new_user and new_pass:
                        success, message = register_user(new_user, new_pass)
                        if success:
                            st.success(f"✅ {message}")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                    else:
                        st.warning("Please enter username and password")
            
            db.close()

# Main Application Controller
def main():
    """Main application controller"""
    
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_main_app()

# Run the app
if __name__ == "__main__":
    main()