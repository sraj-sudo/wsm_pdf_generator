import streamlit as st
from database import init_db
import hashlib

def initialize_authentication():
    """Initialize authentication system"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def login_form():
    """Display login form"""
    st.title("WSM Dashboard Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            db = init_db()
            cursor = db.connection.cursor()
            
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
                         (username, hash_password(password)))
            user = cursor.fetchone()
            cursor.close()
            
            if user:
                st.session_state.authenticated = True
                st.session_state.username = user[1]  # username
                st.session_state.role = user[4]      # role
                st.success(f"Welcome {user[1]}!")
                st.rerun()
            else:
                st.error("Invalid username or password")

def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None
    st.rerun()

def require_auth():
    """Require authentication to access page"""
    if not st.session_state.authenticated:
        login_form()
        st.stop()

def create_user(username, password, email, role='user'):
    """Create new user (admin function)"""
    db = init_db()
    cursor = db.connection.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
            (username, hash_password(password), email, role)
        )
        db.connection.commit()
        cursor.close()
        return True
    except Exception as e:
        st.error(f"Error creating user: {e}")
        return False