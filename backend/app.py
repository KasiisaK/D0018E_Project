# API ENDPOINTS:
#
# CUSTOMER ENDPOINTS:
#
# GET    /products
#        Retrieves a list of all available products.
#
# DELETE /cart/remove
#        Removes a product from a user's shopping cart.
#        Request body (JSON):
#        {
#            "user_id": int,
#            "product_id": int,
#        }
#
# POST   /cart/add
#        Adds a product to a user's shopping cart (can be used to decrament quantity if quantity is negative).
#        Request body (JSON):
#        {
#            "user_id": int,
#            "product_id": int,
#            "quantity": int
#        }
# PUT    /cart/setQuantity
#        Sets the quantity of a specific product in a user's shopping cart.
#
# GET    /cart/<user_id>
#        Retrieves the contents of a specific user's cart,
#
# POST   /orders/create
#        Creates an order from the items in a user's cart.
#        Request body (JSON):
#        {
#            "user_id": int
#        }
#
# GET    /orders/get/<order_id>
#        Retrieves the details of a specific order.
#
# GET    /orders/purchased-products/<user_id>
#        Retrieves a list of all products that a user has purchased (Used when flagging if a user is eligible for commenting on products).
#
#
# ADMIN ENDPOINTS:
# POST   /admin/products/add
#        Adds a new product to the store.
#     Request body (JSON):
#       {
#         "name": string,
#         "description": string,
#         "price": int,
#         "stock_quantity": int,
#         "image_url": string
#       }
# DELETE /admin/products/<product_id>
#        Deletes a product from the store.

# TODO: get max items, for use in max="" in cart later


from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from db import get_db_connection

app = Flask(__name__)
cors = CORS(app) # allow CORS for all domains on all routes.
app.config['CORS_HEADERS'] = 'Content-Type'

# ===============================
# Customer Endpoints
# ===============================

# -------------------------------
# GET PRODUCTS
# -------------------------------
@app.route('/products', methods=['GET'])
@cross_origin()
def get_products():
    print("Received request to get products")
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    cursor.close()
    con.close()

    return jsonify(products)

# -------------------------------
# REMOVE ITEM FROM CART
# -------------------------------
@app.route('/cart/remove', methods=['DELETE'])
@cross_origin()
def remove_from_cart():
    data = request.json
    user_id = data['user_id']
    product_id = data['product_id']

    con = get_db_connection()
    cursor = con.cursor()

    cursor.execute("""
        DELETE FROM cartitems
        WHERE user_id = %s AND product_id = %s
    """, (user_id, product_id))

    con.commit()
    cursor.close()
    con.close()

    return jsonify({"message": "Item removed"}), 200



# -------------------------------
# ADD PRODUCT TO CART
# will check if the item already exists in the cart, 
# if it does, it will update the quantity, otherwise it will insert a new record.
# Also can't go past the stock quantity (set to max if)
# -------------------------------
@app.route('/cart/add', methods=['POST'])
@cross_origin()
def add_to_cart():
    data = request.json
    user_id = data['user_id']
    product_id = data['product_id']
    quantity = data['quantity']

    con = get_db_connection()
    cursor = con.cursor()

    # Check if item already exists
    cursor.execute("""
        SELECT quantity FROM cartitems
        WHERE user_id = %s AND product_id = %s
    """, (user_id, product_id))

    existing = cursor.fetchone()

    # Get max stock for the product
    cursor.execute("""
        SELECT stock_quantity FROM products
        WHERE product_id = %s
    """, (product_id,))
    max_stock = cursor.fetchone()

    if existing:
        # Adjust quantity to not exceed stock
        current_quantity = existing[0]
        
        new_quantity = current_quantity + quantity
        if new_quantity > max_stock[0]:
            quantity = max_stock[0] - current_quantity  

        # Update quantity if not maxced out
        cursor.execute("""
            UPDATE cartitems
            SET quantity = quantity + %s
            WHERE user_id = %s AND product_id = %s
        """, (quantity, user_id, product_id))
    else:
        # Insert new item (if it doesn't exist (first time thing))
        cursor.execute("""
            INSERT INTO cartitems (user_id, product_id, quantity)
            VALUES (%s, %s, %s)
        """, (user_id, product_id, quantity))

    con.commit()
    cursor.close()
    con.close()

    return jsonify({"message": "Cart updated"}), 200

# -------------------------------
# SET ITEM QUANTITY
# -------------------------------
@app.route('/cart/setQuantity', methods=['PUT'])
@cross_origin()
def set_quantity():
    data = request.json
    user_id = data['user_id']
    product_id = data['product_id']
    quantity = data['quantity']

    con = get_db_connection()
    cursor = con.cursor()

    # Get max stock for the product
    cursor.execute("""
        SELECT stock_quantity FROM products
        WHERE product_id = %s
    """, (product_id,))
    max_stock = cursor.fetchone()

    # If quantity exceeds max stock, set it to max stock
    if quantity > max_stock[0]:
        quantity = max_stock[0]

    # Set quantity of a users cart item to a specific value (used for directly setting the quantity from the cart page)
    cursor.execute("""
        UPDATE cartitems
        SET quantity = %s
        WHERE user_id = %s AND product_id = %s
    """, (quantity, user_id, product_id))

    con.commit()
    cursor.close()
    con.close()

    return jsonify({"message": "Quantity set"}), 200


# -------------------------------
# VIEW USER CART
# -------------------------------
@app.route('/cart/<int:user_id>', methods=['GET'])
@cross_origin()
def view_cart(user_id):
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)

    query = """
    SELECT 
        p.product_id,
        p.name,
        p.image_url,
        c.quantity,
        p.price,
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


# -------------------------------
# CREATE ORDER FROM CART
# -------------------------------
@app.route('/orders/create', methods=['POST'])
@cross_origin()
def create_order():
    data = request.json
    user_id = data['user_id']

    con = get_db_connection()
    cursor = con.cursor(dictionary=True)

    # Get user_id's cart items
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


# -------------------------------
# VIEW USER ORDER
# -------------------------------
@app.route('/orders/get/<int:order_id>', methods=['GET'])
@cross_origin()
def get_order_details(order_id):
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)

    # Use JOIN to do everything in one query
    cursor.execute("""
        SELECT p.name, oi.quantity, oi.price_at_purchase,
               (oi.quantity * oi.price_at_purchase) AS total
        FROM orderitems oi
        JOIN products p ON oi.product_id = p.product_id
        WHERE oi.order_id = %s
    """, (order_id,))

    items = cursor.fetchall()

    cursor.close()
    con.close()

    return jsonify(items)

# -------------------------------
# GET ALL ORDERS FROM USER
# -------------------------------
@app.route('/orders/purchased-products/<int:user_id>', methods=['GET'])
@cross_origin()
def get_purchased_products(user_id):
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)

    # Use JOIN to get products and DISTINCT to only get each product once
    cursor.execute("""
        SELECT DISTINCT 
            p.product_id,
            p.name,
            p.price,
            p.image_url
        FROM orders o
        JOIN orderitems oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        WHERE o.user_id = %s
    """, (user_id,))

    products = cursor.fetchall()

    cursor.close()
    con.close()

    return jsonify(products)


# ===============================
# Admin Endpoints
# ===============================

# -------------------------------
# ADD PRODUCT
# -------------------------------
@app.route('/admin/products/add', methods=['POST'])
@cross_origin()
def add_product():
    data = request.json

    name = data['name']
    description = data['description']
    price = data['price']
    stock_quantity = data['stock_quantity']
    image_url = data.get('image_url', None)

    con = get_db_connection()
    cursor = con.cursor()

    cursor.execute("""
        INSERT INTO products (name, description, price, stock_quantity, image_url)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, description, price, stock_quantity, image_url))

    con.commit()
    cursor.close()
    con.close()

    return jsonify({"message": "Product added"}), 201


# -------------------------------
# DELETE PRODUCT
# -------------------------------
@app.route('/admin/products/<int:product_id>', methods=['DELETE'])
@cross_origin()
def delete_product(product_id):
    con = get_db_connection()
    cursor = con.cursor()

    # First, we need to remove the product from any carts before deleting it from the products table
    cursor.execute("""
        DELETE FROM cartitems
        WHERE product_id = %s
    """, (product_id,))

    cursor.execute("""
        DELETE FROM orderitems
        WHERE product_id = %s
    """, (product_id,))

    cursor.execute("""
        DELETE FROM products
        WHERE product_id = %s
    """, (product_id,))

    con.commit()
    cursor.close()
    con.close()

    return jsonify({"message": "Product deleted"}), 200

# Keep at the boottom of the file
if __name__ == '__main__':
    app.run(debug=True)
