import streamlit as st
import team5
import base64
import sys
import os
# هذا الكود يجعل الصفحة تبحث عن الملفات في المجلد الخارجي أيضاً
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- إعداد الخلفية (كما في كودك الأصلي) ---
def get_base64(file):
    try:
        with open(file, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return ""

img = get_base64("images/login_bg.jpg") # تأكد من الامتداد الصحيح للصورة

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{img}");
        background-size: cover; 
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title(":orange[*Login & Sign Up*]")

# زر للعودة للصفحة الرئيسية (Team 3)
if st.button("⬅️ Back to Home Page"):
    st.switch_page("Homepage.py")

st.write("---")

menu = ["Login", "Sign Up"]
choice = st.radio("Choose Option", menu)

# ========================
# LOGIN FORM
# ========================
if choice == "Login":
    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button(":orange[*Login*]"):
        user = team5.login_check(username, password)
        if user:
            # 1. حفظ حالة المستخدم في الجلسة (Session)
            st.session_state['logged_in'] = True
            st.session_state['user_id'] = user['id']
            st.session_state['username'] = user['username']
            st.session_state['role'] = user['role']
            
            st.success(f"Welcome {user['username']}!")
            
            # 2. التوجيه حسب الصلاحية
            if user['role'] == "admin":
                st.switch_page("pages/Admin_Dashboard.py") # استخدام المسار الكامل، أو pages/Admin_Dashboard.py لو أعدت تسميته
                st.rerun() 
            else:
                st.switch_page("Homepage.py") 
                st.rerun()
        else:
            st.error("Invalid username or password")

# ========================
# SIGN UP FORM
# ========================
else:
    st.subheader("Create New Account")

    username = st.text_input("New Username")
    password = st.text_input("New Password", type="password")

    if st.button(":red[*Sign Up*]"):
        if team5.register_user(username, password, role='user'): # الافتراضي مستخدم عادي
            st.success("Account created successfully! Please Login now.")
        else:
            st.error("Username already exists. Try another one.")
