# API ENDPOINTS:
#
# CUSTOMER ENDPOINTS:
#
# GET    /products
#        Retrieves a list of all available products.
#
# POST   /cart/add
#        Adds a product to a user's shopping cart.
#        Request body (JSON):
#        {
#            "user_id": int,
#            "product_id": int,
#            "quantity": int
#        }
#
# GET    /cart/<user_id>
#        Retrieves the contents of a specific user's cart,
#


from flask import Flask, jsonify, request
from db import get_db_connection

app = Flask(__name__)

# -------------------------------
# GET PRODUCTS
# -------------------------------
@app.route('/products', methods=['GET'])
def get_products():
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    cursor.close()
    con.close()

    return jsonify(products)


# -------------------------------
# ADD PRODUCT TO CART
# -------------------------------
@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    data = request.json
    user_id = data['user_id']
    product_id = data['product_id']
    quantity = data['quantity']

    con = get_db_connection()
    cursor = con.cursor()

    # Placeholder (%s) used to stop SQL injection.
    query = """
    INSERT INTO cartitems (user_id, product_id, quantity)
    VALUES (%s, %s, %s)
    """
    cursor.execute(query, (user_id, product_id, quantity))

    con.commit()
    cursor.close()
    con.close()

    return jsonify({"message": "Item added to cart"}), 201


# -------------------------------
# VIEW USER CART
# -------------------------------
@app.route('/cart/<int:user_id>', methods=['GET'])
def view_cart(user_id):
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)

    query = """
    SELECT p.name, c.quantity, p.price,
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


if __name__ == '__main__':
    app.run(debug=True)
