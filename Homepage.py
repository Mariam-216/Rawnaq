import streamlit as st
import team5
import sqlite3 
import base64
import time

# --- Helper Function for Base64 Encoding ---
def img_to_base64(image_path):
    """Converts a local image file to a Base64 string for direct embedding in HTML/CSS."""
    try:
        if image_path.lower().endswith(('.png', '.gif')):
            mime_type = 'image/png'
        elif image_path.lower().endswith(('.jpeg', '.jpg')):
            mime_type = 'image/jpeg'
        else:
            mime_type = 'image/jpeg' 
            
        with open(image_path, "rb") as img_file:
            base64_string = base64.b64encode(img_file.read()).decode()
            return f"data:{mime_type};base64,{base64_string}"
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error converting image {image_path}: {e}")
        return None
# ------------------------------------------

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Fashion Brand", layout="wide")
def set_bg_image(image_path):
    try:
        with open(image_path, "rb") as f:
            data = f.read()
        bin_str = base64.b64encode(data).decode()
        
        page_bg_img = f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* تحسين شكل صور المنتجات */
        .product-img {{
            width: 100%;
            height: 250px;
            object-fit: cover;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.3);
        }}
        
        /* تحسين الكارد */
        .product-card {{
            padding: 12px;
            border-radius: 16px;
            background: rgba(0,0,0,0.45);
            backdrop-filter: blur(6px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            transition: 0.2s;
        }}
        .product-card:hover {{
            transform: scale(1.03);
            box-shadow: 0 6px 18px rgba(0,0,0,0.6);
        }}

        h1, h2, h3, h4, p, span, div {{
            text-shadow: 2px 2px 4px #000000;
        }}
        </style>
        """
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"⚠️ صورة الخلفية غير موجودة في المسار: {image_path}")

# حط هنا مسار الصورة اللي انت عاوزها تكون خلفية
set_bg_image('images/bg2.jpg')
# ==========================================
def apply_custom_style():
    st.markdown("""
        <style>
        /* General styling */
        </style>
    """, unsafe_allow_html=True)

apply_custom_style()
# ==========================================

def init_data_fix():
    try:
        import init_db
    except:
        pass

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT OR IGNORE INTO categories (id, name) VALUES (1, 'Men')")
        cursor.execute("INSERT OR IGNORE INTO categories (id, name) VALUES (2, 'Women')")
        conn.commit()
    except:
        pass

    existing_products = team5.get_all_products()
    if not existing_products:
        team5.add_product("Classic Shirt", 1, "M", "White", 450.0, 10, "images/shirt.jpg") 
        team5.add_product("Slim Jeans", 1, "32", "Blue", 600.0, 15, "images/jeans.jpg")
        team5.add_product("Summer Dress", 2, "S", "Red", 750.0, 8, "images/dresss.jpg")
        team5.add_product("Brown Dress", 2, "OneSize", "Brown", 950.0, 20, "images/handbag (1).jpg")

    conn.close()

init_data_fix()

# ==========================================

# --- Initializing Session State ---
if 'page' not in st.session_state:
    st.session_state['page'] = 'home'
if 'selected_cat_id' not in st.session_state:
    st.session_state['selected_cat_id'] = None
if 'selected_product' not in st.session_state:
    st.session_state['selected_product'] = None
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None 
if 'checkout_status' not in st.session_state: 
    st.session_state['checkout_status'] = 'idle'


def go_to(page_name):
    st.session_state['page'] = page_name
    st.rerun()

# --- Login/Logout Functions ---
def logout_user():
    st.session_state['user_id'] = None 
    st.session_state['page'] = 'home'
    st.toast("Logged out successfully!")
    st.rerun()

def login_user_simulated(user_id=1):
    st.switch_page("Register.py")
# -----------------------------

# ==========================================

def render_home():
    st.markdown("<h1 style='text-align: center; color: #000000;'> RAWNAQ BRAND </h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>Style for Men & Women</h4>", unsafe_allow_html=True)
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("👔 SHOP MEN COLLECTION", use_container_width=True):
            st.session_state['selected_cat_id'] = 1
            go_to('category')
    with col2:
        if st.button("👗 SHOP WOMEN COLLECTION", use_container_width=True):
            st.session_state['selected_cat_id'] = 2
            go_to('category')

    st.write("")
    
def render_category():
    # 1. زرار الرجوع والعنوان
    cat_id = st.session_state['selected_cat_id']
    cat_name = "Men" if cat_id == 1 else "Women"

    if st.button("⬅️ Back to Home"):
        go_to('home')

    st.title(f"{cat_name} Section")

    # 2. جلب المنتجات
    # Get products fresh every time to reflect stock updates
    all_products = team5.get_all_products() 
    base_products = [p for p in all_products if p['category_id'] == cat_id]

    if not base_products:
        st.warning("لا توجد منتجات حالياً!")
        return

    # 3. نظام الفلتر (القائمة المنسدلة + السعر)
    with st.expander("🔍 Filter & Search (تصفية المنتجات)", expanded=False):
        c_filter1, c_filter2 = st.columns(2)
        
        with c_filter1:
            filter_options = ["الكل", "Shirt", "Jeans", "Dress", "T-shirt", "Shoes"]
            selected_type = st.selectbox("اselect product :", filter_options)

        with c_filter2:
            # فلتر السعر (سلايدر)
            prices = [p['salary'] for p in base_products]
            if prices:
                min_p, max_p = int(min(prices)), int(max(prices))
                # Adjust range if min and max are the same
                if min_p == max_p: 
                    min_p = max(0, min_p - 100)
                    max_p = max_p + 100
                    
                price_range = st.slider(" Price Range (EGP)", min_p, max_p, (min_p, max_p))
            else:
                price_range = (0, 10000)

    # 4. تطبيق الفلتر
    final_products = []
    for p in base_products:
        # أ) تصفية بالسعر
        if not (price_range[0] <= p['salary'] <= price_range[1]):
            continue
        
        # ب) تصفية بالنوع (القائمة المنسدلة)
        if selected_type != "الكل":
            if selected_type.lower() not in p['name'].lower():
                continue
            
        final_products.append(p)

    # 5. عرض المنتجات النهائية
    if not final_products:
        st.info(f"لا توجد منتجات من نوع '{selected_type}' في هذا النطاق السعري.")
    else:
        st.caption(f"تم العثور على {len(final_products)} منتج")
        
        cols = st.columns(4)
        for i, product in enumerate(final_products):
            with cols[i % 4]:
                st.markdown("<div class='product-card'>", unsafe_allow_html=True)

                image_data_url = img_to_base64(product['image'])
                if image_data_url:
                    st.markdown(f"<img src='{image_data_url}' class='product-img'/>", unsafe_allow_html=True)
                else:
                    st.write("❌ No Image") 

                st.subheader(product['name'])
                st.write(f"**{product['salary']} EGP**")
                
                # Fetch stock dynamically
                stock = product.get('stock', 0)
                st.write(f"**Stock:** {stock}")

                if stock and stock > 0:
                    if st.button("Add 🛒", key=f"add_{product['id']}", use_container_width=True):
                        user_id = st.session_state.get('user_id') 
                        if user_id:
                            team5.add_to_cart(user_id, product['id'], 1)
                            st.toast("تمت الإضافة للسلة! 🛒")
                        else:
                            st.warning("يجب تسجيل الدخول أولاً")
                            time.sleep(3)
                            st.switch_page("pages/Register.py")
                else:
                    st.button("Sold Out", disabled=True, use_container_width=True)

                if st.button("Details 📄", key=f"view_{product['id']}", use_container_width=True):
                    st.session_state['selected_product'] = product
                    go_to('product')

                st.markdown("</div>", unsafe_allow_html=True)
                
def render_product():
    if st.button("⬅️ Back"):
        go_to('category')

    product = st.session_state['selected_product']
    if not product:
        return

    # Use data from session state for simplicity
    stock = product.get('stock', 0) 

    c1, c2 = st.columns([1, 1])
    with c1:
        image_data_url = img_to_base64(product['image'])
        if image_data_url:
            st.markdown(
                f"<img src='{image_data_url}' class='product-img'/>",
                unsafe_allow_html=True
            )
        else:
            st.error("Product image failed to load.")

    with c2:
        st.title(product['name'])
        st.subheader(f"{product['salary']} EGP")
        
        st.write(f"**Stock:** {stock}")
        st.divider()

        desc = f"""
        - Color: {product['color']}
        - Size: {product['size']}
        - Premium Cotton Material
        """
        st.info(desc)

        size = st.selectbox("Choose Size", ["S", "M", "L", "XL", "XXL"])
        
        # Limit quantity to available stock
        max_qty = int(stock) if isinstance(stock, int) else 10
        qty = st.number_input("Quantity", 1, max_qty, 1)

        if stock and stock > 0:
            if st.button("Add to Cart 🛒"):
                user_id = st.session_state.get('user_id') 
                if user_id:
                    team5.add_to_cart(user_id, product['id'], qty)
                    st.success(f"Added {qty} item(s) to cart!")
                    st.rerun() 
                else:
                    st.warning("Please log in to add items to your cart.")
        else:
            st.button("Sold Out", disabled=True, use_container_width=True)


def render_cart():
    user_id = st.session_state.get('user_id')

    st.title("🛒 Your Cart")
    
    # --- 1. HANDLE POST-CHECKOUT SUCCESS ---
    if st.session_state['checkout_status'] == 'success':
        st.balloons()
        st.success("🎉 Payment successful! Your order has been placed!")
        
        time.sleep(3) 
        
        # After delay, redirect to home page and reset status
        st.session_state['checkout_status'] = 'idle'
        go_to('home')
        return

    # --- 2. HANDLE CHECKOUT PENDING (The state showing "Redirecting...") ---
    if st.session_state['checkout_status'] == 'pending_redirect':
        st.info("✅ Redirecting to external payment page (Simulated)...") 
        
        time.sleep(1) 
        
        # *** CRITICAL CHANGE: Use the transactional function ***
        if user_id:
            # This calls the function that updates stock AND clears the cart
            if team5.process_order_and_update_stock(user_id):
                st.session_state['checkout_status'] = 'success'
            else:
                # Stock error or DB transaction failure
                st.error("Error processing order. Check stock levels or user login status and try again.")
                st.session_state['checkout_status'] = 'idle' # Go back to idle state
        else:
            st.error("User ID not found. Cannot process order.")
            st.session_state['checkout_status'] = 'idle'
        
        # Trigger the rerun to render the 'success' or error state
        st.rerun()
        return

    # --- 3. HANDLE IDLE (Default cart display) ---
    if st.button("⬅️ Back to Shopping"):
        st.session_state['checkout_status'] = 'idle'
        go_to('home')

    if not user_id:
        st.info("You must be logged in to view your cart.")
        return

    items = team5.view_cart(user_id)

    if not items:
        st.info("Your cart is empty.")
        return

    total = 0

    # Display Cart Items
    for item in items:
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([1, 2, 1, 1])
            with c1:
                image_data_url = img_to_base64(item['image'])
                if image_data_url:
                    st.markdown(
                        f"<img src='{image_data_url}' width='80'/>",
                        unsafe_allow_html=True
                    )
                else:
                    st.write("No Image")

            with c2:
                st.subheader(item['name'])
                st.caption(f"Qty: {item['quantity']}")
                
                # Simple check: Cart quantity vs current stock (User friendly warning)
                if item.get('stock', 0) < item['quantity']:
                    st.error(f"⚠️ **Stock Warning:** Only {item.get('stock', 0)} available!")

            with c3:
                item_total = item['salary'] * item['quantity']
                total += item_total
                st.write(f"**{item_total} EGP**")

            with c4:
                # Use cart_item_id to remove the correct entry
                if st.button("Remove ❌", key=f"del_{item['cart_item_id']}"): 
                    team5.remove_from_cart(item['cart_item_id'])
                    st.rerun()

    st.divider()
    st.subheader(f"Total: {total} EGP")

    if st.button("Checkout 💳", type="primary"):
        # Set the state to 'pending_redirect' and force a rerun
        st.session_state['checkout_status'] = 'pending_redirect'
        st.switch_page("pages/Payment.py")

# ==========================================
## 🔑 Render Login/Signup Page (Simulated Redirect)
# ==========================================
def render_login():
    st.title("🔑 Account Access")
    st.write("---")

    st.header("External Login / Sign Up")
    st.info("""
        Click the button below to **Login** or **Create a New Account** on our secure account portal.
    """)
    
    if st.button("Go to Login/Sign Up Page ➡️", use_container_width=True, type="primary"):
        st.success("SIMULATED REDIRECT: Redirecting to your custom login page...")
        
        st.warning("Simulating successful login back to the app...")
        login_user_simulated(user_id=1)
        
# ==========================================
## 👤 Render Profile Page (FIXED)
# ==========================================

def render_profile():
    if st.button("⬅️ Back to Home"):
        go_to('home')
        
    st.title("👤 My Profile")
    st.write("Manage your personal details, security settings, and view your order history.")
    st.divider()

    user_id = st.session_state.get('user_id')
    
    if not user_id:
        st.error("You are not logged in.")
        return

    # --- Simulated User Data ---
    user_data = {
        'id': user_id,
        'name': 'Ahmed Salah' if user_id == 1 else 'New User', 
        'password_mask': '********' 
    }
    
    # ==========================
    # 1. Personal Details Section
    # ==========================
    st.header("Personal Details")
    st.markdown(f"**Name:** {user_data['name']}")
    
    st.subheader("Update Name")
    with st.form("update_name_form"):
        new_name = st.text_input("New Name", value=user_data['name'])
        if st.form_submit_button("Update Name"):
            st.success(f"Name updated successfully to: {new_name} (Simulated)")
            
    st.divider()

    # ==========================
    # 2. Security Section 
    # ==========================
    st.header("🔒 Security")
    st.markdown(f"**Current Password:** {user_data['password_mask']}")
    
    st.subheader("Change Password")
    with st.form("change_password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.form_submit_button("Change Password"):
            if new_password != confirm_password:
                st.error("New Password and Confirmation Password do not match.")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                st.success("Password changed successfully! (Simulated)")

    st.divider()

    # ==========================
    # 3. Order History Section (IMPROVED DISPLAY WITH st.table)
    # ==========================
   # st.header("📦 Order History")
    
   # history = team5.get_order_history(user_id)
    
   # if history:
       # for order in history:
            # Use an expander for better organization
          #  with st.expander(f"Order **#{order['id']}** | Total: **{order['total']} EGP** | Status: **{order['status']}**", expanded=False):
              #  st.caption(f"Date Placed: {order['date']}")
                
             #   st.markdown("##### Ordered Products:")
                
                # --- THIS PART USES st.table FOR CLEARER DISPLAY ---
            #    order_data = []
           #     for item in order['items']:
          #          order_data.append([
         #               item['name'],                   # Product Name
        #                item['qty'],                    # Quantity Ordered
       #                 f"{item['price']} EGP"          # Price at time of order
      #              ])
                
     #           st.table([["Product Name", "Qty", "Price"]] + order_data) # Add header row
                # ----------------------------------------------------
                
    #else:
     #   st.info("You have no past orders.")
    #    
   # st.divider()
    
    # Logout button at the very bottom
    if st.button("➡️ **Logout**", use_container_width=True, type="primary"):
        logout_user()

# ==========================================
## ℹ️ Render About Us Page (UPDATED)
# ==========================================

def render_about():
    st.title("ℹ️ About RAWNAQ BRAND")
    st.write("---")
    
    st.header("Our Story and Vision")
    st.write("""
        RAWNAQ BRAND was founded on the principle of providing **high-quality, stylish fashion** that is accessible to everyone. 
        We believe that clothing is more than just fabric—it's a form of **self-expression**.
    """)
    
    st.header("Quality and Materials")
    st.write("""
        We are committed to **sustainability** and **ethical sourcing**. All our garments are crafted 
        from premium materials, including organic cotton and recycled fibers, ensuring durability and comfort.
    """)
    
    st.divider()
    
    # --- Contact and Social Media Section (Part 1) ---
    col_contact1, col_contact2 = st.columns(2)
    
    with col_contact1:
        st.subheader("📍 Contact Info")
        st.markdown("**📞 Phone:** +20 1022826895") 
        st.markdown("**🏢 Address:** Cairo, Egypt")
        st.markdown("**📧 Email:** team3@example.com")
        
    with col_contact2:
        st.subheader("📱 Social Media")
        st.link_button("📸 Instagram", "https://www.instagram.com/rawnaq_shop28")
        st.link_button("🎵 TikTok", "https://www.tiktok.com/@rawnaq_shop_")
    
    st.divider()
    
    # --- Team Information Section (Part 2) ---
    st.header("👥 Development Teams")
    main_col1, main_col2 = st.columns(2)
    
    # ==========================
    # Team 3: Frontend & UI
    # ==========================
    with main_col1:
        
        
        t3_boys, t3_girls = st.columns(2)
        
        # 1. Boys Column
        with t3_boys:
            st.markdown("Boys staff")
            st.markdown("""
            * [Ahmed helmy ]
            * [Ammar Yasser ]
            * [Abdelrhman Ashraf ]
            * [Ahmed Saber ]
            * [Ahmed Mohammad ]
            """)
            
        # 2. Girls Column
        with t3_girls:
            st.markdown("Girls Staff")
            st.markdown("""
            * [Rokaya Alaa ]
            * [Mariam Osama]
            * [Maya Seraj ]
            * [Lynah Adel ]
            * [Walaa Magdy]
            """)
            
    # ==========================
    # Team 5: Database & Backend (Placeholder)
    # ==========================
    with main_col2:
        st.info("💾 Team 5: Database & Backend") 
        st.markdown("Details for Team 5 members go here.")
    
    st.divider()
    
    # Back button
    if st.button("⬅️ Back to Home"):
        go_to('home')     

# ==========================================

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3081/3081559.png", width=100)
    st.title("Menu")

    if st.button("🏠 Home Page"):
        go_to('home')

    user_is_logged_in = st.session_state.get('user_id') is not None

    if user_is_logged_in:
        # LOGGED IN VIEW
        if st.button("👤 My Profile"):
            go_to('profile')

        cart_count = 0
        try:
            cart_count = len(team5.view_cart(st.session_state['user_id']))
        except Exception as e:
            pass 
            
        if st.button(f"🛒 My Cart ({cart_count})"):
            go_to('cart')
            
        st.divider()
        if st.button("➡️ Logout", use_container_width=True):
            logout_user()

    else:
        # LOGGED OUT VIEW
        if st.button("🔑 **Login / Sign Up**", use_container_width=True, type="primary"):
            st.switch_page("pages/Register.py")
            
    st.divider()

    if st.button("ℹ️ About Us"):
        go_to('about')

    

# Page routing
if st.session_state['page'] == 'home':
    render_home()
elif st.session_state['page'] == 'category':
    render_category()
elif st.session_state['page'] == 'product':
    render_product()
elif st.session_state['page'] == 'cart':
    render_cart()
elif st.session_state['page'] == 'profile': 
    render_profile()
elif st.session_state['page'] == 'login': 
    render_login()
elif st.session_state['page'] == 'about':
    render_about()
