import streamlit as st
import team5 # Import the updated db module
import sqlite3 
import base64
import time

# --- Helper Function for Base64 Encoding ---
def img_to_base64(image_path):
    """Converts a local image file to a Base64 string for direct embedding in HTML/CSS."""
    try:
        # Determine MIME type
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

        h1, h2, h3, h4, p, span, div, .stSelectbox label, .stSlider label {{
            color: white; /* Ensure text is visible on dark background */
            text-shadow: 2px 2px 4px #000000;
        }}
        </style>
        """
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"⚠️ صورة الخلفية غير موجودة في المسار: {image_path}")

# حط هنا مسار الصورة اللي انت عاوزها تكون خلفية
set_bg_image('images/bg2.jpg') # Ensure this path is correct
# ==========================================

def apply_custom_style():
    # You can add more global styles here if needed
    st.markdown("""
        <style>
        /* Placeholder for additional global styles */
        </style>
    """, unsafe_allow_html=True)

apply_custom_style()
# ==========================================

# NOTE: This block assumes 'init_db.py' exists and sets up the tables properly.
# The `db` module already includes the table creation logic.
def init_data_fix():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    # 1. Ensure categories exist
    try:
        cursor.execute("INSERT OR IGNORE INTO categories (id, name) VALUES (1, 'Men')")
        cursor.execute("INSERT OR IGNORE INTO categories (id, name) VALUES (2, 'Women')")
        conn.commit()
    except:
        pass

    # 2. Ensure initial products exist
    existing_products = team5.get_all_products()
    if not existing_products or len(existing_products) < 4:
        # NOTE: Added a 'stock' column assumption here.
        team5.add_product("Classic Shirt", 1, "M", "White", 450.0, 10, "images/shirt.jpg") 
        team5.add_product("Slim Jeans", 1, "32", "Blue", 600.0, 15, "images/jeans.jpg")
        team5.add_product("Summer Dress", 2, "S", "Red", 750.0, 8, "images/dress.jpeg")
        team5.add_product("Brown Dress", 2, "OneSize", "Brown", 950.0, 20, "images/dress2.jpg")

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
if 'checkout_status' not in st.session_state: # <-- Check status for staged checkout
    st.session_state['checkout_status'] = 'idle'


def go_to(page_name):
    st.session_state['page'] = page_name
    st.rerun()
if 'checkout_status' not in st.session_state:
    st.session_state['checkout_status'] = 'idle'

# --- ضيف السطرين دول تحت السطر اللي فوق ده علطول ---
if 'my_orders' not in st.session_state:
    st.session_state['my_orders'] = []
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
    st.markdown("<h1 style='text-align: center; color: white;'> RAWNAQ BRAND </h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: white;'>Style for Men & Women</h4>", unsafe_allow_html=True)
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
    all_products = team5.get_all_products()
    base_products = [p for p in all_products if p['category_id'] == cat_id]

    if not base_products:
        st.warning("لا توجد منتجات حالياً!")
        return

    # ==========================================
    # 3. نظام الفلتر (القائمة المنسدلة + السعر)
    # ==========================================
    with st.expander("🔍 Filter & Search (تصفية المنتجات)", expanded=False):
        c_filter1, c_filter2 = st.columns(2)
        
        with c_filter1:
            # --- التعديل هنا: قائمة منسدلة بدل الكتابة ---
            filter_options = ["الكل", "Shirt", "Jeans", "Dress", "T-shirt", "Shoes"]
            selected_type = st.selectbox("Select product type:", filter_options)

        with c_filter2:
            # فلتر السعر (سلايدر)
            prices = [p['salary'] for p in base_products]
            if prices:
                min_p, max_p = int(min(prices)), int(max(prices))
                # Handle case where min and max are the same
                if min_p == max_p: 
                    min_p = 0
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

    # ==========================================
    # 5. عرض المنتجات النهائية
    # ==========================================
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
                
                # Use .get() for safer access
                stock = product.get('stock', 0)
                st.write(f"**Stock:** {stock}")

                if stock and stock > 0:
                    if st.button("Add 🛒", key=f"add_{product['id']}", use_container_width=True):
                        user_id = st.session_state.get('user_id') 
                        if user_id:
                            # Use product['id'] as product_id for the database
                            team5.add_to_cart(user_id, product['id'], 1)
                            st.toast("تمت الإضافة للسلة! 🛒")
                            st.rerun()
                        else:
                            st.warning("يجب تسجيل الدخول أولاً")
                            st.switch_page("Register.py")
                # --- Corrected Code Snippet for render_category ---
# ... inside the loop over final_products ...
                else:
                    st.button(
                        "Sold Out", 
                        disabled=True, 
                        use_container_width=True,
                        # FIX: Add a unique key here
                        key=f"soldout_{product['id']}" 
                    )
# ... rest of the loop ...

                if st.button("Details 📄", key=f"view_{product['id']}", use_container_width=True):
                    st.session_state['selected_product'] = product
                    go_to('product')

                st.markdown("</div>", unsafe_allow_html=True)
def render_product():
    if st.button("⬅️ Back"):
        go_to('category')

    product = st.session_state['selected_product']
    if not product:
        st.warning("Product details not found.")
        return

    # In a real app, you would re-fetch the product here to ensure stock is up to date
    # product = db.get_product_by_id(product['id']) 

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
        
        # --- Simplified Stock Display ---
        stock = product.get('stock', 0)
        st.write(f"**Stock:** {stock}")
        st.divider()
        # --------------------------

        desc = f"""
        - Color: {product['color']}
        - Size: {product['size']}
        - Premium Cotton Material
        """
        st.info(desc)

        size = st.selectbox("Choose Size", ["S", "M", "L", "XL", "XXL"])
        
        # Limit quantity to available stock
        max_qty = int(stock) if isinstance(stock, int) and stock > 0 else 1
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
        st.session_state['checkout_status'] = 'idle'
        go_to('home')
        return

    # --- 2. HANDLE CHECKOUT PENDING ---
    if st.session_state['checkout_status'] == 'pending_redirect':
        st.info("✅ Processing order...") 
        time.sleep(1) 
        
        try:
            # 1. هات الحاجات اللي في السلة دلوقتي
            cart_items = team5.view_cart(user_id)
            
            if cart_items:
                # 2. احسب التوتال واسماء المنتجات عشان نحفظهم في الهيستوري
                total_price = sum(item['salary'] * item['quantity'] for item in cart_items)
                items_names = ", ".join([f"{item['name']} (x{item['quantity']})" for item in cart_items])
                
                # 3. احفظ الاوردر في الذاكرة (session_state)
                new_order = {
                    "id": int(time.time()), # رقم عشوائي للطلب بناء على الوقت
                    "date": time.strftime("%Y-%m-%d"),
                    "total": total_price,
                    "status": "Processing ⏳",
                    "items": items_names
                }
                # دي الخطوة اللي بتسمع في البروفايل
                st.session_state['my_orders'].append(new_order) 

                # 4. خصم المخزون (لو الدالة موجودة عندك)
                # for item in cart_items:
                #    db.update_product_stock(item['product_id'], item['quantity'])
            
            # 5. فضي السلة
            team5.clear_cart(user_id) 
            st.session_state['checkout_status'] = 'success'
            st.rerun()

        except Exception as e:
            st.error(f"Error processing checkout: {e}")
            st.session_state['checkout_status'] = 'idle'
            st.rerun()
        return

    # --- 3. HANDLE IDLE (عرض السلة العادية) ---
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
    for item in items:
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([1, 2, 1, 1])
            with c1:
                image_data_url = img_to_base64(item['image'])
                if image_data_url:
                    st.markdown(f"<img src='{image_data_url}' width='80' style='border-radius: 8px;'/>", unsafe_allow_html=True)
                else:
                    st.write("No Image")
            with c2:
                st.subheader(item['name'])
                st.caption(f"Qty: {item['quantity']}")
            with c3:
                item_total = item['salary'] * item['quantity']
                total += item_total
                st.write(f"**{item_total} EGP**")
            with c4:
                if st.button("Remove ❌", key=f"del_{item['id']}"):
                    team5.remove_from_cart(item['id'])
                    st.rerun()

    st.divider()
    st.subheader(f"Total: {total} EGP")

    if st.button("Checkout 💳"):
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
    
    # Simulate redirection to the external page
    if st.button("Go to Login/Sign Up Page ➡️", use_container_width=True, type="primary"):
        st.success("SIMULATED REDIRECT: Redirecting to your custom login page...")
        
        # Simulating successful login back to the app immediately
        st.warning("Simulating successful login back to the app...")
        login_user_simulated(user_id=1) # Logs in a user after the simulated external process
        
# ==========================================
## 👤 Render Profile Page
# ==========================================
def render_profile():
    if st.button("⬅️ Back to Home"):
        go_to('home')
        
    st.title("👤 My Profile")
    st.write("Manage your personal details and security settings.")
    st.divider()

    user_id = st.session_state.get('user_id')
    if not user_id:
        st.error("You are not logged in.")
        return

    # 1. جلب البيانات الحقيقية من الداتا بيز
    current_user_data = team5.get_user_by_id(user_id)
    
    if not current_user_data:
        st.error("User not found in database.")
        return

    # عرض البيانات
    st.header("Personal Details")
    st.markdown(f"**Current Name:** {current_user_data['username']}")
    st.markdown(f"**Role:** {current_user_data['role']}")
    
    st.subheader("Update Name")
    with st.form("update_name_form"):
        new_name = st.text_input("New Name", value=current_user_data['username'])
        
        if st.form_submit_button("Update Name"):
            if new_name and new_name != current_user_data['username']:
                # استدعاء دالة التحديث من db
                if team5.update_username(user_id, new_name):
                    st.success(f"Name updated successfully to: {new_name}")
                    time.sleep(1) # استنى ثانية عشان اليوزر يشوف الرسالة
                    st.rerun()    # اعمل ريفرش عشان الاسم الجديد يظهر
                else:
                    st.error("Username already exists, please choose another one.")
            elif new_name == current_user_data['username']:
                st.warning("No changes made to the name.")
            
    st.divider()

    # ==========================
    # جزء المشتريات السابقة (زي ما هو)
    # ==========================
    st.header("🛍️ Order History (طلباتي السابقة)")
    my_orders = st.session_state.get('my_orders', [])

    if my_orders:
        for order in reversed(my_orders):
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.subheader(f"Order #{order['id']}")
                    st.caption(f"Date: {order['date']}")
                    st.write(f"**Items:** {order['items']}")
                with c2:
                    st.write(f"**{order['total']} EGP**")
                    st.info(order['status'])
    else:
        st.info("No previous orders found yet.")
    # ==========================

    st.divider()

    st.header("Security")
    # بنعمل ماسك للباسورد عشان ميبانش
    masked_pass = "*" * len(str(current_user_data['password']))
    st.markdown(f"**Current Password:** {masked_pass}")
    
    st.subheader("Change Password")
    with st.form("change_password_form"):
        current_password_input = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.form_submit_button("Change Password"):
            # التأكد من الباسورد القديم
            if current_password_input != current_user_data['password']:
                st.error("Incorrect Current Password!")
            elif new_password != confirm_password:
                st.error("New Password and Confirmation Password do not match.")
            elif len(new_password) < 4: # خليتها 4 للتسهيل
                st.error("Password must be at least 4 characters.")
            else:
                # استدعاء دالة تحديث الباسورد من db
                team5.update_password(user_id, new_password)
                st.success("Password changed successfully!")
                time.sleep(1)
                st.rerun()

    st.divider()
    
    if st.button("➡️ **Logout**", use_container_width=True, type="primary"):
        logout_user()
# ==========================================
## ℹ️ Render About Us Page
# ==========================================

def render_about():
    st.title(" About RAWNAQ BRAND")
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
        st.markdown("**🏢 Address:** Menofiya, Egypt")
        st.markdown("**📧 Email:** team@example.com")
        
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
            st.markdown(" Boys staff")
            st.markdown("""
            * [Ahmed helmy ]
            * [Ammar Yasser ]
            * [Abdelrhman Ashraf ]
            * [Ahmed Mohammad ]
            * [Ahmed Saber ]
            """)
            
        # 2. Girls Column
        with t3_girls:
            st.markdown(" Girls staff")
            st.markdown("""
            * [Rokaya Alaa ]
            * [Mariam Osama ]
            * [Maya Seraj ]
            * [Lynah Adel ]
            * [Walaa Magdy ]
            """)
            
    # ==========================
    # Team 5: Database & Backend (Placeholder)
    # ==========================
    
    st.divider()
    
    # Back button
    if st.button("⬅️ Back to Home"):
        go_to('home')       

# ==========================================

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3081/3081559.png", width=100)
    st.title("Menu")

    if st.button(" Home Page"):
        go_to('home')

    user_is_logged_in = st.session_state.get('user_id') is not None

    if user_is_logged_in:
        # LOGGED IN VIEW
        if st.button("👤 My Profile"):
            go_to('profile')

        try:
            # Get cart count dynamically
            cart_count = len(team5.view_cart(st.session_state['user_id']))
        except:
            cart_count = 0
            
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