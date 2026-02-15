from flask import Flask, jsonify
from db import get_db_connection

app = Flask(__name__)


@app.route("/products", methods=["GET"])
def get_products():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(products)


if __name__ == "__main__":
    app.run(debug=True)

