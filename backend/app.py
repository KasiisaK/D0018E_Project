
# Token Decorator:
# Generates a JWT token and used for authentication on protected routes. Checks for token in Authorization header, verifies it, and extracts user ID for use in route handlers.
#
# API enpoints:
# === USER AUTH ENDPOINTS ===
# /api/register - Register new user, returns token for immediate login aswell
# /api/login - Login existing user, returns token
# /api/user - Get current user info (requires auth)
# === PRODUCTS ===
# /products - Get all products
# /product/<id> - Get single product by ID
# === CART (AUTH REQUIRED) ===
# /cart - View cart items
# /cart/add - Add item to cart (will add to existing quantity if item already in cart)
# /cart/setQuantity - Set exact quantity for an item in cart
# /cart/remove - Remove item from cart
# === ORDERS (AUTH REQUIRED) ===
# /orders/create - Create order from cart (will also clear cart and update stock)
# === ADMIN ===
# /admin/products/add - Add new product (no auth for simplicity, but should be protected in real app)


import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS, cross_origin
from db import get_db_connection

from flask_bcrypt import Bcrypt
import jwt
import datetime
from functools import wraps

# ===============================
# CONFIG
# ===============================

SECRET_KEY = os.getenv("SECRET_KEY")

application = Flask(__name__, static_folder="dist", static_url_path="")
CORS(application)

bcrypt = Bcrypt(application)

# ===============================
# TOKEN DECORATOR
# ===============================

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            try:
                token = request.headers["Authorization"].split(" ")[1]
            except:
                return jsonify({"error": "Invalid token header"}), 401

        if not token:
            return jsonify({"error": "Token missing"}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user_id = data["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated

# ===============================
# USER AUTH ENDPOINTS
# ===============================

# ------------------------------
# Register
# will alos return a token so user can be logged in immediately after registration
# ------------------------------

@application.route("/api/register", methods=["POST"])
@cross_origin()
def register_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

    con = get_db_connection()
    cursor = con.cursor()

    cursor.execute(
        "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
        (username, hashed_pw)
    )

    user_id = cursor.lastrowid
    con.commit()
    cursor.close()
    con.close()

    token = jwt.encode({
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({
        "user": {"id": user_id, "username": username},
        "token": token
    }), 201

# ------------------------------
# Login
# ------------------------------
@application.route("/api/login", methods=["POST"])
@cross_origin()
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    con = get_db_connection()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    cursor.close()
    con.close()

    if not user or not bcrypt.check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode({
        "user_id": user["user_id"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({
        "user": {
            "id": user["user_id"],
            "username": user["username"]
        },
        "token": token
    })


# ------------------------------
# Get current user info (AUTH REQUIRED)
# ------------------------------
@application.route("/api/user", methods=["GET"])
@cross_origin()
@token_required
def get_current_user():
    user_id = request.user_id

    con = get_db_connection()
    cursor = con.cursor(dictionary=True)

    cursor.execute(
        "SELECT user_id, username FROM users WHERE user_id = %s",
        (user_id,)
    )
    user = cursor.fetchone()

    cursor.close()
    con.close()

    return jsonify({"user": user})


# ===============================
# PRODUCTS
# ===============================

@application.route("/products", methods=["GET"])
@cross_origin()
def get_products():
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    cursor.close()
    con.close()

    return jsonify(products)

# ------------------------------
# Get single product by ID
# ------------------------------
@application.route("/product/<int:product_id>", methods=["GET"])
@cross_origin()
def get_product(product_id):
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM products WHERE product_id = %s",
        (product_id,)
    )
    product = cursor.fetchone()

    cursor.close()
    con.close()

    return jsonify(product)


# ===============================
# CART (AUTH REQUIRED)
# ===============================

@application.route("/cart", methods=["GET"])
@cross_origin()
@token_required
def view_cart():
    user_id = request.user_id

    con = get_db_connection()
    cursor = con.cursor(dictionary=True)

    query = """
    SELECT p.product_id, p.name, p.image_url,
           c.quantity, p.price,
           (c.quantity * p.price) AS total
    FROM cartitems c
    JOIN products p ON c.product_id = p.product_id
    WHERE c.user_id = %s
    """

    cursor.execute(query, (user_id,))
    cart = cursor.fetchall()

    cursor.close()
    con.close()

    return jsonify(cart)

# ------------------------------
# Add to cart (will add to existing quantity if item already in cart)
# ------------------------------
@application.route("/cart/add", methods=["POST"])
@cross_origin()
@token_required
def add_to_cart():
    data = request.json
    user_id = request.user_id
    product_id = data["product_id"]
    quantity = data["quantity"]

    con = get_db_connection()
    cursor = con.cursor()
    
    # Check if item already exists
    cursor.execute("""
        SELECT quantity FROM cartitems
        WHERE user_id = %s AND product_id = %s
    """, (user_id, product_id))

    existing = cursor.fetchone()

    if existing:
        new_quantity = existing[0] + quantity
        cursor.execute("""
            UPDATE cartitems
            SET quantity = %s
            WHERE user_id = %s AND product_id = %s
        """, (new_quantity, user_id, product_id))
    else:
        cursor.execute("""
            INSERT INTO cartitems (user_id, product_id, quantity)
            VALUES (%s, %s, %s)
        """, (user_id, product_id, quantity))

        
    con.commit()
    cursor.close()
    con.close()

    return jsonify({"message": "Cart updated"}), 200

@application.route("/cart/setQuantity", methods=["PUT"])
@cross_origin()
@token_required
def set_cart_quantity():
    data = request.json
    user_id = request.user_id
    product_id = data["product_id"]
    quantity = data["quantity"]

    con = get_db_connection()
    cursor = con.cursor()

    cursor.execute("""
        UPDATE cartitems
        SET quantity = %s
        WHERE user_id = %s AND product_id = %s
    """, (quantity, user_id, product_id))

    con.commit()
    cursor.close()
    con.close()

    return jsonify({"message": "Cart updated"})

@application.route("/cart/remove", methods=["DELETE"])
@cross_origin()
@token_required
def remove_from_cart():
    data = request.json
    user_id = request.user_id
    product_id = data["product_id"]

    con = get_db_connection()
    cursor = con.cursor()

    cursor.execute(
        "DELETE FROM cartitems WHERE user_id = %s AND product_id = %s",
        (user_id, product_id)
    )

    con.commit()
    cursor.close()
    con.close()

    return jsonify({"message": "Item removed from cart"})

# ===============================
# ORDERS (AUTH REQUIRED)
# ===============================

# ------------------------------
# Create order from cart (will also clear cart and update stock)
# ------------------------------
@application.route('/orders/create', methods=['POST'])
@cross_origin()
@token_required
def create_order():
    user_id = request.user_id

    con = get_db_connection()
    cursor = con.cursor(dictionary=True)

    # Get users' cart items
    cursor.execute("""
        SELECT c.product_id, c.quantity, p.price
        FROM cartitems c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id = %s
    """, (user_id,))
    
    cart_items = cursor.fetchall()

    # Chack if bad request (cart is empty)
    if not cart_items:
        return jsonify({"message": "Cart is empty"}), 400

    # Create order (use Pending (forever), since no payment or delivery)
    cursor.execute("""
        INSERT INTO orders (user_id, order_date, status)
        VALUES (%s, NOW(), 'Pending')
    """, (user_id,))
    
    order_id = cursor.lastrowid # Returns ^ INSERT
    
    # Insert order items from cart
    for item in cart_items:
        cursor.execute("""
            INSERT INTO orderitems 
            (order_id, product_id, quantity, price_at_purchase)
            VALUES (%s, %s, %s, %s)
        """, (
            order_id,
            item['product_id'],
            item['quantity'],
            item['price']
        ))

    # Clear cart
    cursor.execute("""
        DELETE FROM cartitems WHERE user_id = %s
    """, (user_id,))

    con.commit()
    cursor.close()
    con.close()

    return jsonify({
        "message": "Order created",
        "order_id": order_id
    }), 201



# ===============================
# ADMIN
# ===============================

# ------------------------------
# Add new product (no auth for simplicity, but should be protected in real app)
# ------------------------------

@application.route("/admin/products/add", methods=["POST"])
@cross_origin()
def add_product():
    data = request.json

    con = get_db_connection()
    cursor = con.cursor()

    cursor.execute("""
        INSERT INTO products (name, description, price, stock_quantity, image_url)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        data["name"],
        data["description"],
        data["price"],
        data["stock_quantity"],
        data.get("image_url")
    ))

    con.commit()
    cursor.close()
    con.close()

    return jsonify({"message": "Product added"}), 201


# ===============================
# SERVE VUE SPA
# ===============================

@application.route("/", defaults={"path": ""})
@application.route("/<path:path>")
def serve_vue(path):
    if path != "" and os.path.exists(os.path.join(application.static_folder, path)):
        return send_from_directory(application.static_folder, path)
    return send_from_directory(application.static_folder, "index.html")


if __name__ == "__main__":
    application.run(debug=True)