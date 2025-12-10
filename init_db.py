import sqlite3

def create_database():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # USERS TABLE

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        phone TEXT UNIQUE,
        address TEXT,
        role TEXT
    )
    """)

    # CATEGORIES

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )
    """)

    # PRODUCTS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER,
        name TEXT,
        size TEXT,
        color TEXT,
        salary REAL,
        stock INTEGER,
        image TEXT,
        FOREIGN KEY(category_id) REFERENCES categories(id)
    )
    """)

    # CART

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )
    """)

    # ORDERS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        total REAL,
        payment_method TEXT,
        status TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # PAYMENT TABLE

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        card_number TEXT,
        cvv TEXT,
        expire_date TEXT,
        FOREIGN KEY(order_id) REFERENCES orders(id)
    )
    """)

    # FEEDBACK

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()
    print("DATABASE CREATED SUCCESSFULLY!")


create_database()