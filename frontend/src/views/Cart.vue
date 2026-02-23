<template>
  <div class="container">
    <div class="breadcrumb">
      <router-link to="/">Home</router-link> / <span>Cart</span>
    </div>

    <h1 class="section-title">Your Cart</h1>

    <!-- EMPTY CART -->
    <div v-if="cartStore.items.length === 0" class="empty-cart">
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
          <tr v-for="item in cartStore.items" :key="item.product_id">
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
                v-model.number="item.quantity"
                @change="cartStore.updateQuantity(item.product_id, item.quantity)"
                class="quantity-input"
              >
            </td>

            <td>
              ${{ (item.price * item.quantity).toFixed(2) }}
            </td>

            <td>
              <button
                @click="cartStore.removeItem(item.product_id)"
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
          <span>Subtotal ({{ cartStore.totalItems }} items)</span>
          <span>${{ cartStore.totalPrice.toFixed(2) }}</span>
        </div>

        <div class="summary-row">
          <span>Shipping</span>
          <span>Free</span>
        </div>

        <div class="summary-row total">
          <span>Total</span>
          <span>${{ cartStore.totalPrice.toFixed(2) }}</span>
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
import { useCartStore } from '../stores/cart'

export default {
  setup() {
    const cartStore = useCartStore()

    cartStore.fetchCart(1)

    return { cartStore }
  },

  methods: {
    fakeOrder() {
      alert('Order placed! (not really, this is just a demo)')
      this.cartStore.createOrder(1)
    }
  }

}
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