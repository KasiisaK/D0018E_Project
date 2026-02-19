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
