<template>
  <div class="container">
    <div class="breadcrumb">
      <router-link to="/">Home</router-link> / <span>Cart</span>
    </div>

    <h1 class="section-title">Your Cart</h1>

    <!-- EMPTY CART -->
    <div v-if="cartItems.length === 0" class="empty-cart">
      <p>Your cart is empty.</p>
      <router-link to="/products" class="btn">Continue Shopping</router-link>
    </div>

    <!-- CART CONTENT -->
    <div v-else class="cart-content">
      <table class="cart-table">
        <thead>
          <tr>
            <th>Product</th>
            <th>Price</th>
            <th>Quantity</th>
            <th>Total</th>
            <th></th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="item in cartItems" :key="item.product_id">
            <td class="product-info">
              <img
                :src="item.image_url"
                :alt="item.name"
                class="cart-product-image"
              >
              <span>{{ item.name }}</span>
            </td>

            <td>${{ Number(item.price).toFixed(2) }}</td>

            <td>
              <input
                type="number"
                min="1"
                :max="getMaxStock(item.product_id)"                 
                v-model.number="item.quantity"
                @change="setQuantity(item)"
                class="quantity-input"
              >
            </td>

            <td>
              ${{ (item.price * item.quantity).toFixed(2) }}
            </td>

            <td>
              <button
                @click="removeItem(item.product_id)"
                class="remove-btn"
              >
                ✕
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- SUMMARY -->
      <div class="cart-summary">
        <h3>Order Summary</h3>

        <div class="summary-row">
          <span>Subtotal ({{ totalItems }} items)</span>
          <span>${{ totalPrice.toFixed(2) }}</span>
        </div>

        <div class="summary-row">
          <span>Shipping</span>
          <span>Free</span>
        </div>

        <div class="summary-row total">
          <span>Total</span>
          <span>${{ totalPrice.toFixed(2) }}</span>
        </div>

        <button class="btn order-btn" @click="fakeOrder">
          Place Order
        </button>

        <p class="fake-note">(fake, no actual order will be placed)</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";


/*
Loads the cart at startup
then methods: include updating quantity and removing items.
*/
export default {
  data() {
    return {
      cartItems: [], // Initialize cartItems as an empty list
      products: [] // Get products for max_quantity in the quantity input
    };
  },

  async created() {
    const response = await axios.get("http://127.0.0.1:5000/cart/1"); //Hardcoded user_id=1 for demo purposes
    this.cartItems = response.data;  // set the data
    const response2 = await axios.get("http://127.0.0.1:5000/products");
    this.products = response2.data;
  },

  // Dynamically calculate total items and total price based on cartItems
  computed: {
    totalItems() {
      return this.cartItems.reduce((sum, item) => sum + item.quantity, 0);
    },

    totalPrice() {
      return this.cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0);
    }
  },

  // Methods to update quantity and remove items from the cart
  methods: {
    async setQuantity(item) {
      try {
        await axios.put("http://127.0.0.1:5000/cart/setQuantity", {
          user_id: 1,
          product_id: item.product_id,
          quantity: item.quantity
        });
      } catch (error) {
        console.error(error);
      }
    },

    async removeItem(productId) {
      await axios.delete("http://127.0.0.1:5000/cart/remove", {
        data: {
          user_id: 1, //hardcoded for now as user_id = 1
          product_id: productId
        }
      });

      // Remove the item from the local cartItems list to update the UI
      this.cartItems = this.cartItems.filter(
        item => item.product_id !== productId
      );
    },

    // Helper method to get the maximum stock quantity for a product (used in "max" in the quantity input)
    getMaxStock(product_id) {
      const product = this.products.find(p => p.product_id === product_id);
      return product ? product.stock_quantity : 1;
    },

    fakeOrder() {
      alert("Order placed! (not really)");
    }
  }
};
</script>


<style scoped>
.cart-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 40px;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.cart-table th {
  background: #2c3e50;
  color: white;
  padding: 15px;
  text-align: left;
  font-weight: 600;
}

.cart-table td {
  padding: 20px 15px;
  border-bottom: 1px solid #ecf0f1;
  color: #2c3e50;
}

.product-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.cart-product-image {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 8px;
}

.quantity-input {
  width: 70px;
  padding: 8px;
  border: 1px solid #bdc3c7;
  border-radius: 4px;
  text-align: center;
}

.remove-btn {
  background: none;
  border: none;
  color: #e74c3c;
  font-size: 1.2rem;
  cursor: pointer;
  transition: color 0.2s;
}

.remove-btn:hover {
  color: #c0392b;
}

.cart-summary {
  background: white;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  max-width: 400px;
  margin-left: auto;
}

.cart-summary h3 {
  margin-bottom: 20px;
  color: #2c3e50;
  font-size: 1.5rem;
  border-bottom: 1px solid #ecf0f1;
  padding-bottom: 10px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  color: #34495e;
}

.summary-row.total {
  font-size: 1.3rem;
  font-weight: 700;
  color: #2c3e50;
  border-top: 2px solid #ecf0f1;
  padding-top: 15px;
  margin-top: 10px;
}

.order-btn {
  width: 100%;
  margin-top: 20px;
  background-color: #c71818;
}

.order-btn:hover {
  background-color: #151518;
}

.fake-note {
  text-align: center;
  margin-top: 15px;
  font-size: 0.9rem;
  color: #7f8c8d;
  font-style: italic;
}

.empty-cart {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.empty-cart p {
  font-size: 1.2rem;
  color: #2c3e50;
  margin-bottom: 20px;
}

@media (max-width: 768px) {
  .cart-table, .cart-table thead, .cart-table tbody, .cart-table tr, .cart-table td {
    display: block;
  }
  
  .cart-table thead {
    display: none;
  }
  
  .cart-table tr {
    margin-bottom: 20px;
    border: 1px solid #ecf0f1;
    border-radius: 8px;
    overflow: hidden;
  }
  
  .cart-table td {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px;
    border-bottom: 1px solid #ecf0f1;
  }
  
  .cart-table td:last-child {
    border-bottom: none;
  }
  
  .cart-table td::before {
    content: attr(data-label);
    font-weight: 600;
    color: #2c3e50;
  }
  
  .product-info {
    width: 100%;
  }
  
  .cart-summary {
    max-width: 100%;
  }
}
</style>