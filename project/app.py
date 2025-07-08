import streamlit as st
import json
import os
import hashlib
import datetime
from typing import Optional, List, Dict, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from models.bank_system import BankSystem
from models.user import User
from models.account import Account
from models.transaction import Transaction
from utils.auth import AuthManager
from utils.data_manager import DataManager
from components.admin_panel import AdminPanel
from components.customer_panel import CustomerPanel
from components.analytics import Analytics

# Page configuration
st.set_page_config(
    page_title="Bank Management System",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4 0%, #2ca02c 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        font-size: 2rem;
        font-weight: bold;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .sidebar-content {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #1f77b4 0%, #2ca02c 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .stSelectbox > div > div {
        background: white;
        border-radius: 5px;
        border: 1px solid #e0e0e0;
    }
    
    .stTextInput > div > div > input {
        background: white;
        border-radius: 5px;
        border: 1px solid #e0e0e0;
    }
    
    .stNumberInput > div > div > input {
        background: white;
        border-radius: 5px;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'bank_system' not in st.session_state:
        st.session_state.bank_system = BankSystem()
    if 'auth_manager' not in st.session_state:
        st.session_state.auth_manager = AuthManager()

def login_page():
    """Display login page"""
    st.markdown('<div class="main-header">🏦 Bank Management System</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Login")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_button = st.form_submit_button("Login", use_container_width=True)
            
            if login_button:
                if username and password:
                    user = st.session_state.auth_manager.authenticate_user(username, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user_id = user.user_id
                        st.session_state.user_role = user.role
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.error("Please fill in all fields")
        
        st.markdown("---")
        st.subheader("Register New Account")
        
        with st.form("register_form"):
            reg_username = st.text_input("Username", placeholder="Choose a username", key="reg_username")
            reg_password = st.text_input("Password", type="password", placeholder="Choose a password", key="reg_password")
            reg_email = st.text_input("Email", placeholder="Enter your email", key="reg_email")
            reg_phone = st.text_input("Phone", placeholder="Enter your phone number", key="reg_phone")
            reg_role = st.selectbox("Role", ["customer", "admin"], key="reg_role")
            register_button = st.form_submit_button("Register", use_container_width=True)
            
            if register_button:
                if reg_username and reg_password and reg_email and reg_phone:
                    if st.session_state.auth_manager.register_user(reg_username, reg_password, reg_email, reg_phone, reg_role):
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error("Username already exists")
                else:
                    st.error("Please fill in all fields")

def main_app():
    """Main application after login"""
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f'<div class="sidebar-content">', unsafe_allow_html=True)
        st.title("Navigation")
        
        user = st.session_state.auth_manager.get_user(st.session_state.user_id)
        if user:
            st.write(f"Welcome, {user.username}!")
            st.write(f"Role: {user.role.title()}")
        
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.session_state.user_role = None
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content based on user role
    if st.session_state.user_role == "admin":
        admin_panel = AdminPanel(st.session_state.bank_system, st.session_state.auth_manager)
        admin_panel.display()
    else:
        customer_panel = CustomerPanel(st.session_state.bank_system, st.session_state.auth_manager, st.session_state.user_id)
        customer_panel.display()

def main():
    """Main application function"""
    initialize_session_state()
    
    if not st.session_state.authenticated:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()