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

    <!-- Cart Content -->
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
                :max="getMaxStock(item.product_id) ?? 9999"
                :value="item.quantity"
                @input="handleQuantityInput(item, $event)"
                @change="handleQuantityChange(item)"
                class="quantity-input"
              >
            </td>

            <td>
              ${{ (item.price * item.quantity).toFixed(2) }}
            </td>

            <td>
              <button
                @click="removeItemFromList(item)"
                class="remove-btn"
              >
                ✕
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Order Summary -->
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

        <!-- Demo mode note – will be replaced by receipt modal -->
        <p class="fake-note">(Demo mode: no actual payment)</p>
      </div>
    </div>
  </div>

  <!-- Order Receipt Modal -->
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

// Receipt modal state
const showReceipt = ref(false)
const lastOrder = ref({
  orderId: null,
  items: [],
  total: 0
})

// Load product catalog once for stock validation
onMounted(async () => {
  try {
    const res = await api.get('/products')
    products.value = res.data
  } catch (err) {
    // Silently fail – stock check will simply have no limit
  }

  // Load cart if user is logged in
  if (authStore.isAuthenticated) {
    await cartStore.fetchCart()
  }
  loading.value = false
})

// Get maximum allowed quantity from product stock
function getMaxStock(productId) {
  const product = products.value.find(p => p.product_id === productId)
  return product && typeof product.stock === 'number' ? product.stock : null
}

// Handle quantity input changes (client-side validation)
function handleQuantityInput(item, event) {
  let newQty = parseInt(event.target.value, 10)

  // Enforce minimum 1
  if (isNaN(newQty) || newQty < 1) {
    newQty = 1
  }

  // Enforce stock limit if available
  const maxStock = getMaxStock(item.product_id)
  if (maxStock !== null && maxStock > 0 && newQty > maxStock) {
    newQty = maxStock
    alert(`Only ${maxStock} available in stock!`)
  }

  // Update local quantity only if changed
  if (item.quantity !== newQty) {
    item.quantity = newQty
  }
}

// Sync quantity with backend when input loses focus
async function handleQuantityChange(item) {
  await cartStore.updateQuantity(item.product_id, item.quantity)
}

// Remove item from cart
async function removeItemFromList(item) {
  await cartStore.removeItem(item.product_id)
}

// Place order – show receipt on success
async function placeOrder() {
  if (!authStore.isAuthenticated) {
    alert('Please log in to place an order')
    return
  }

  // Snapshot current cart before clearing
  const orderedItems = cartStore.items.map(item => ({ ...item }))
  const orderTotal = cartStore.totalPrice

  try {
    const orderId = await cartStore.createOrder()  // this clears cart store
    // Show receipt modal with order details
    lastOrder.value = {
      orderId,
      items: orderedItems,
      total: orderTotal
    }
    showReceipt.value = true
  } catch (err) {
    alert('Failed to place order')
    console.error(err)
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
  gap: 16px;
  min-height: 90px;
}

.cart-product-image {
  width: 110px;
  height: 110px;
  object-fit: cover;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
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