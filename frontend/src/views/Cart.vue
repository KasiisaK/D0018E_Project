<template>
  <div class="container">
    <!-- Breadcrumb -->
    <div class="breadcrumb">
      <router-link to="/">Home</router-link> / <span>Cart</span>
    </div>

    <h1 class="section-title">Your Cart</h1>

    <!-- Empty Cart State -->
    <div v-if="cartStore.items.length === 0" class="empty-cart">
      <p>Your cart is empty.</p>
      <router-link to="/products" class="btn">Continue Shopping</router-link>
    </div>

    <!-- Cart Content (cards layout) -->
    <div v-else class="cart-layout">
      <!-- Left column: cart items as cards -->
      <div class="cart-items">
        <div
          v-for="item in cartStore.items"
          :key="item.product_id"
          class="cart-item-card"
        >
          <img
            :src="item.image_url"
            :alt="item.name"
            class="cart-item-image"
          >
          <div class="cart-item-details">
            <h3 class="cart-item-name">{{ item.name }}</h3>
            <p class="cart-item-price">${{ Number(item.price).toFixed(2) }}</p>
            <div class="cart-item-controls">
              <div class="quantity-wrapper">
                <label for="quantity">Qty:</label>
                <input
                  type="number"
                  min="1"
                  :max="getMaxStock(item.product_id) ?? 9999"
                  :value="item.quantity"
                  @input="handleQuantityInput(item, $event)"
                  @change="handleQuantityChange(item)"
                  class="quantity-input"
                >
              </div>
              <button
                @click="removeItemFromList(item)"
                class="remove-btn"
                title="Remove item"
              >
                ✕
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Right column: Order Summary -->
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
        <button class="btn order-btn" @click="placeOrder">
          Place Order
        </button>
        <p class="fake-note">(no actual payment)</p>
      </div>
    </div>
  </div>

  <!-- Order Receipt -->
  <OrderReceipt
    :show="showReceipt"
    :orderId="lastOrder.orderId"
    :items="lastOrder.items"
    :total="lastOrder.total"
    @close="showReceipt = false"
  />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useCartStore } from '../stores/cart'
import { useAuthStore } from '../stores/auth'
import api from '../api/index'
import OrderReceipt from '../components/OrderReceipt.vue'

const cartStore = useCartStore()
const authStore = useAuthStore()

const products = ref([])
const loading = ref(true)
const showReceipt = ref(false)
const lastOrder = ref({ orderId: null, items: [], total: 0 })

onMounted(async () => {
  try {
    const res = await api.get('/products')
    products.value = res.data
  } catch (err) {
    // Silently fail
  }
  if (authStore.isAuthenticated) {
    await cartStore.fetchCart()
  }
  loading.value = false
})

function getMaxStock(productId) {
  const product = products.value.find(p => p.product_id === productId)
  return product && typeof product.stock === 'number' ? product.stock : null
}

function handleQuantityInput(item, event) {
  let newQty = parseInt(event.target.value, 10)
  if (isNaN(newQty) || newQty < 1) newQty = 1
  const maxStock = getMaxStock(item.product_id)
  if (maxStock !== null && maxStock > 0 && newQty > maxStock) {
    newQty = maxStock
    alert(`Only ${maxStock} available in stock!`)
  }
  if (item.quantity !== newQty) {
    item.quantity = newQty
  }
}

async function handleQuantityChange(item) {
  await cartStore.updateQuantity(item.product_id, item.quantity)
}

async function removeItemFromList(item) {
  await cartStore.removeItem(item.product_id)
}

async function placeOrder() {
  if (!authStore.isAuthenticated) {
    alert('Please log in to place an order')
    return
  }
  const orderedItems = cartStore.items.map(item => ({ ...item }))
  const orderTotal = cartStore.totalPrice
  try {
    const orderId = await cartStore.createOrder()
    lastOrder.value = { orderId, items: orderedItems, total: orderTotal }
    showReceipt.value = true
  } catch (err) {
    alert('Failed to place order')
    console.error(err)
  }
}
</script>

<style scoped>
.cart-layout {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 30px;
  margin-top: 30px;
}

.cart-items {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.cart-item-card {
  display: flex;
  background: #2b2a33;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s, box-shadow 0.2s;
  color: white;
}

.cart-item-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
}

.cart-item-image {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-right: 2px solid #3a3944;
}

.cart-item-details {
  flex: 1;
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.cart-item-name {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: white;
}

.cart-item-price {
  font-size: 1.1rem;
  color: #4caf50;
  font-weight: 500;
  margin: 0 0 12px 0;
}

.cart-item-controls {
  display: flex;
  align-items: center;
  gap: 16px;
  min-height: 90px;
}

.quantity-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quantity-wrapper label {
  color: #dddddd;
  font-size: 0.9rem;
}

.quantity-input {
  width: 70px;
  padding: 6px 8px;
  border: 1px solid #575569;
  border-radius: 6px;
  background-color: #1e1e24;
  color: white;
  text-align: center;
  font-size: 0.95rem;
}

.quantity-input:focus {
  outline: none;
  border-color: #4caf50;
}

.remove-btn {
  background: none;
  border: none;
  color: #ff6b6b;
  font-size: 1.4rem;
  cursor: pointer;
  line-height: 1;
  padding: 0 5px;
  transition: color 0.2s;
}

.remove-btn:hover {
  color: #ff8a8a;
}

.cart-summary {
  background: #2b2a33;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  color: white;
  height: fit-content;
  position: sticky;
  top: 20px;
}

.cart-summary h3 {
  margin-bottom: 20px;
  color: white;
  font-size: 1.5rem;
  border-bottom: 1px solid #3a3944;
  padding-bottom: 10px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  color: #dddddd;
}

.summary-row.total {
  font-size: 1.3rem;
  font-weight: 700;
  color: white;
  border-top: 2px solid #3a3944;
  padding-top: 15px;
  margin-top: 10px;
}

.order-btn {
  width: 100%;
  margin-top: 20px;
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.order-btn:hover {
  background-color: #45a049;
}

.fake-note {
  text-align: center;
  margin-top: 15px;
  font-size: 0.9rem;
  color: #aaaaaa;
  font-style: italic;
}

.empty-cart {
  text-align: center;
  padding: 60px 20px;
  background: #2b2a33;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  color: white;
}

.empty-cart p {
  font-size: 1.2rem;
  margin-bottom: 20px;
}

.empty-cart .btn {
  background: #4caf50;
  color: white;
  padding: 10px 20px;
  text-decoration: none;
  border-radius: 6px;
  display: inline-block;
}

.empty-cart .btn:hover {
  background: #45a049;
}

@media (max-width: 768px) {
  .cart-layout {
    grid-template-columns: 1fr;
  }

  .cart-summary {
    position: static;
    margin-top: 20px;
  }

  .cart-item-card {
    flex-direction: column;
  }

  .cart-item-image {
    width: 100%;
    height: 180px;
    border-right: none;
    border-bottom: 2px solid #3a3944;
  }

  .cart-item-details {
    padding: 16px;
  }
}
</style>