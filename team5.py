import sqlite3

DB_NAME = "database.db"


def get_connection():

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ================================================
#   TEAM 1 => FUNCTIONS (LOGIN / REGISTER)
# ================================================

def register_user(username, password, role='user'):

    # LOGIN NEW USER

    try:
        conn = get_connection()
        conn.execute("INSERT INTO users (username, password,  role) VALUES (?, ?, ?)",
                     (username, password, role))
        conn.commit()
        conn.close()
        return True                  # REGISTER SUCCESSFULLY
    except sqlite3.IntegrityError:
        return False                 # USERNAME REPEATED

def initialize_admin_user():
    """يسجل مستخدم الأدمن الافتراضي مرة واحدة فقط."""
    conn = get_connection()
    user_exists = conn.execute("SELECT * FROM users WHERE username='admin'").fetchone()
    conn.close()

    if not user_exists:
        # هنا يمكنكِ تحديد بيانات الأدمن التي تفضلينها
        # يجب أن تكون هذه البيانات هي التي ستستخدمينها لتسجيل الدخول
        if register_user("admin", "admin123", "admin"):
            print("INFO: Default admin user 'admin' created successfully.")
            
# نقوم بتشغيل هذه الدالة مباشرة عند استيراد team5
initialize_admin_user()


def login_check(username, password):

      # CHECK LOGIN PROCESS

    conn = get_connection()
    # نطلب من قاعدة البيانات البحث عن مستخدم يطابق الاسم والرقم السري ورقم الهاتف معاً
    user = conn.execute("SELECT * FROM users WHERE username=? AND password=?",
                        (username, password)).fetchone()
    conn.close()
    
    if user:
        return dict(user)  # RETURN DATA OF USER
    return None           # INVALID DATAا


def validate_egyptian_phone_number(phone):
    eg_network = ['010', '011', '012', '015']

    if len(phone) != 11:
        return False
    if not phone.isdigit():
        return False
    if phone[:3] not in eg_network:
        return False
    

    return True


# =========================================================
#       TEAM 2 FUNCTIONS (ADMIN DASHBOARD + CRUD PRODUCTS)
# =========================================================

def add_product(name, category_id, size, color, salary, stock, image_path):

 # ADD NEW PRODUCT

    conn = get_connection()
    conn.execute("""
                    INSERT INTO products (name, category_id, size, color, salary, stock, image)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (name, category_id, size, color, salary, stock, image_path))
    conn.commit()
    conn.close()


def edit_product(product_id, name, salary, stock):

    # EDIT PRODUCT

    conn = get_connection()
    conn.execute("UPDATE products SET name=?, salary=?, stock=? WHERE id=?",
                 (name, salary, stock, product_id))
    conn.commit()
    conn.close()


def delete_product(product_id):

    # DELETE PRODUCT

    conn = get_connection()
    conn.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()


def get_all_products():

    #VIEW PRODUCT

    conn = get_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return [dict(row) for row in products]


# =============================================
#   TEAM 3 FUNCTIONS (USER HOME + CART SYSTEM)
# =============================================

def get_products_for_home():

      # VIEW PRODUCTS IN HOME PAGE

    return get_all_products()           # SAME VIEW FUNCTION


def add_to_cart(user_id, product_id, quantity=1):

    # ADD NEW CART

    conn = get_connection()
    # Check if product is already in cart, if so, update quantity
    cursor = conn.execute("SELECT * FROM cart WHERE user_id=? AND product_id=?", 
                          (user_id, product_id)).fetchone()
    
    if cursor:
        # If product exists, increment quantity
        new_qty = dict(cursor)['quantity'] + quantity
        conn.execute("UPDATE cart SET quantity=? WHERE user_id=? AND product_id=?", 
                     (new_qty, user_id, product_id))
    else:
        # If product is new, insert
        conn.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)",
                     (user_id, product_id, quantity))
    
    conn.commit()
    conn.close()


def view_cart(user_id):

    # VIEW CART PRODUCTS (Modified to return product_id)

    conn = get_connection()

    query = """
             SELECT cart.id, cart.product_id, products.name, products.salary, cart.quantity, products.image
             FROM cart
                      JOIN products ON cart.product_id = products.id
             WHERE cart.user_id = ? 
             """
    items = conn.execute(query, (user_id,)).fetchall()
    conn.close()
    return [dict(row) for row in items]


def remove_from_cart(cart_id):

    #REMOVE PRODUCTS FROM CART

    conn = get_connection()
    conn.execute("DELETE FROM cart WHERE id=?", (cart_id,))
    conn.commit()
    conn.close()

# --- NEW FUNCTIONS FOR CHECKOUT/STOCK MANAGEMENT ---

def update_product_stock(product_id, quantity_to_subtract):
    """Safely decrements the stock for a given product ID by the purchased quantity."""
    conn = get_connection()
    # Ensure stock doesn't go below zero (though cart validation should prevent this)
    conn.execute(
        "UPDATE products SET stock = MAX(0, stock - ?) WHERE id = ?",
        (quantity_to_subtract, product_id)
    )
    conn.commit()
    conn.close()
    
def clear_cart(user_id):
    """Removes all items from a user's cart after a successful checkout."""
    conn = get_connection()
    conn.execute("DELETE FROM cart WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

# ====================================================
#   TEAM 4 FUNCTIONS (Payment + Feedback)
# ====================================================

def save_payment(order_id, card_number, cvv, expire_date):

    #SAVE PAYMENT METHOD *VISA*

    conn = get_connection()
    conn.execute("INSERT INTO payment (order_id, card_number, cvv, expire_date) VALUES (?, ?, ?, ?)",
                 (order_id, card_number, cvv, expire_date))
    conn.commit()
    conn.close()

def update_user_address(user_id, address):
    
    #UPDATE USER ADDRESS DURING CHECKOUT
    
    conn = get_connection()
    conn.execute("UPDATE users SET address=? WHERE id=?", (address, user_id))
    conn.commit()
    conn.close()


def save_feedback(user_id, message):

    #SAVE FEEDBACK

    conn = get_connection()
    conn.execute("INSERT INTO feedback (user_id, message) VALUES (?, ?)",
                 (user_id, message))
    conn.commit()
    conn.close()
# ===================================
# ====================================================
#   NEW FUNCTIONS: USER PROFILE MANAGEMENT (Add this to db.py)
# ====================================================

def get_user_by_id(user_id):
    """Get user details by ID to show in profile."""
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def update_username(user_id, new_username):
    """Update the username in the database."""
    try:
        conn = get_connection()
        conn.execute("UPDATE users SET username=? WHERE id=?", (new_username, user_id))
        conn.commit()
        conn.close()
        return True # Success
    except sqlite3.IntegrityError:
        return False # Username already taken

def update_password(user_id, new_password):
    """Update the password in the database."""
    conn = get_connection()
    conn.execute("UPDATE users SET password=? WHERE id=?", (new_password, user_id))
    conn.commit()
    conn.close()

# ===================================
# TESTING (TO MAKE SURE OUR JOB IS DONE HERE , **3BDO && 3MMAR** <3)
# ===================================
if __name__ == "__main__":
    print("✅ Team 5: Testing Database Functions...")

    # 1. Test Register
    if register_user("admin", "admin123", "01000000000","admin"):
        print("    -> Admin User Created Successfully")
    else:
        print("    -> User already exists")

    # 2. Test Login
    user = login_check("admin", "admin123")
    if user:
        print(f"    -> Login Verified for: {user['username']} (Role: {user['role']})")
        
    # 3. Test Stock Update (Example for product ID 1)
    # update_product_stock(1, 2)
    # print("    -> Simulated: Stock for product 1 decremented by 2.")

    print("✅ Team 5 Tasks Completed: DB Setup + CRUD Functions Ready.")