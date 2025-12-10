import streamlit as st
import pandas as pd
from PIL import Image
import time
import team5 
import sys
import os
# هذا الكود يجعل الصفحة تبحث عن الملفات في المجلد الخارجي أيضاً
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- إعدادات الصفحة ---
try:
    st.set_page_config(page_title="Admin Dashboard", layout="wide")
except:
    pass

# === Security Check (حماية الصفحة) ===
if 'role' not in st.session_state or st.session_state['role'] != 'admin':
    st.warning("⛔ Access Denied! You are not an admin.")
    if st.button("Go to Login"):
        st.switch_page("pages/Register.py")
    st.stop() # إيقاف تنفيذ باقي الكود

IMAGE_DIR = "product_images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# --- دوال مساعدة ---
def save_uploaded_file(uploaded_file, product_name):
    if uploaded_file:
        file_extension = uploaded_file.name.split('.')[-1]
        timestamp = int(time.time())
        safe_name = "".join([c for c in product_name if c.isalpha() or c.isdigit()]).rstrip()
        file_path = os.path.join(IMAGE_DIR, f"{safe_name}_{timestamp}.{file_extension}")
        img = Image.open(uploaded_file)
        img.save(file_path)
        return file_path
    return None

# --- صفحة الأدمن الرئيسية ---
def admin_page():
    st.title("Admin Dashboard 🔒")
    st.markdown(f"Welcome, **{st.session_state.get('username', 'Admin')}**")
    
    st.sidebar.title("Control Panel")
    
    # === زر تسجيل الخروج ===
    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear() # مسح البيانات
        st.switch_page("pages/Register.py") # العودة لصفحة الدخول

    st.sidebar.write("---")
    
    action = st.sidebar.radio(
        "Choose Operation:",
        ["View All Products", "Add New Product", "Edit Product", "Delete Product"]
    )
    
    CATEGORY_MAP = {"Men": 1, "Women": 2}
    
    # 1. VIEW PRODUCTS
    if action == "View All Products":
        st.header("📦 Current Inventory")
        products = team5.get_all_products()
        if products:
            df = pd.DataFrame(products)
            if not df.empty:
                id_to_name = {v: k for k, v in CATEGORY_MAP.items()}
                if 'category_id' in df.columns:
                    df['category_name'] = df['category_id'].map(id_to_name)
                cols_to_show = ['id', 'name', 'salary', 'stock', 'size', 'color']
                if 'category_name' in df.columns: cols_to_show.append('category_name')
                st.dataframe(df[cols_to_show], use_container_width=True)
                
                st.write("---")
                st.subheader("🖼️ Product Gallery")
                cols = st.columns(4)
                for index, row in df.iterrows():
                    with cols[index % 4]:
                        if row.get('image') and os.path.exists(row['image']):
                            st.image(row['image'], caption=f"{row['name']} - {row['salary']} EGP")
                        else:
                            st.info(f"No Image: {row['name']}")
        else:
            st.info("The database is currently empty.")

    # 2. ADD PRODUCT
    elif action == "Add New Product":
        st.header("➕ Add New Product")
        with st.form("add_product_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Product Name")
                selected_cat_name = st.selectbox("Category", list(CATEGORY_MAP.keys()))
                salary = st.number_input("Price (EGP)", min_value=1.0, step=10.0)
            with col2:
                size = st.selectbox("Size", ["S", "M", "L", "XL", "Free Size"])
                color = st.text_input("Color", "Black")
                stock = st.number_input("Stock Quantity", min_value=1, step=1)
            st.subheader("Product Image")
            uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
            submitted = st.form_submit_button("Save Product", type="primary")
            
            if submitted:
                if name and salary and stock and uploaded_file:
                    final_category_id = CATEGORY_MAP[selected_cat_name]
                    image_path = save_uploaded_file(uploaded_file, name)
                    try:
                        team5.add_product(name, final_category_id, size, color, salary, stock, image_path)
                        st.success(f"✅ Product '{name}' added successfully!")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("⚠️ Please fill all fields.")

    # 3. EDIT PRODUCT
    elif action == "Edit Product":
        st.header("✏️ Edit Product Details")
        products = team5.get_all_products()
        if products:
            product_options = {f"{p['name']} (ID: {p['id']})": p for p in products}
            selected_option = st.selectbox("Select Product", list(product_options.keys()))
            selected_product = product_options[selected_option]
            with st.form("edit_form"):
                new_name = st.text_input("Name", value=selected_product['name'])
                new_salary = st.number_input("Price", value=float(selected_product['salary']))
                new_stock = st.number_input("Stock", value=int(selected_product['stock']))
                if st.form_submit_button("Update Product"):
                    team5.edit_product(selected_product['id'], new_name, new_salary, new_stock)
                    st.success("Product updated successfully!")
                    st.rerun()
        else:
            st.info("No products available.")

    # 4. DELETE PRODUCT
    elif action == "Delete Product":
        st.header("🗑️ Delete Product")
        products = team5.get_all_products()
        if products:
            product_dict = {f"{p['name']} (ID: {p['id']})": p['id'] for p in products}
            selected_name = st.selectbox("Select Product", list(product_dict.keys()))
            if st.button("Permanently Delete", type="primary"):
                product_id = product_dict[selected_name]
                team5.delete_product(product_id)
                st.success("Product deleted.")
                time.sleep(1)
                st.rerun()
        else:
            st.info("No products to delete.")

if __name__ == "__main__":
    admin_page()