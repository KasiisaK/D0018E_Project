<template>
  <div v-if="show" class="modal-overlay" @click.self="close">
    <div class="modal-content">
      <header>
        <h2>Order Receipt</h2>
        <button @click="close" class="close-btn">&times;</button>
      </header>

      <!-- Receipt Content -->
      <div class="receipt">
        <!-- Order Info -->
        <div class="order-info">
          <p><strong>Order ID:</strong> {{ orderId }}</p>
          <p><strong>Date:</strong> {{ orderDate }}</p>
        </div>

        <!-- Items Table -->
        <table class="items-table">
          <thead>
            <tr>
              <th>Product</th>
              <th>Qty</th>
              <th>Price</th>
              <th>Total</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.product_id">
              <td>{{ item.name }}</td>
              <td>{{ item.quantity }}</td>
              <td>${{ Number(item.price).toFixed(2) }}</td>
              <td>${{ (item.quantity * item.price).toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>

        <!-- Totals -->
        <div class="totals">
          <div class="total-row">
            <span>Subtotal:</span>
            <span>${{ subtotal.toFixed(2) }}</span>
          </div>
          <div class="total-row">
            <span>Shipping:</span>
            <span>Free</span>
          </div>
          <div class="total-row grand-total">
            <span>Total:</span>
            <span>${{ total.toFixed(2) }}</span>
          </div>
        </div>

        <!-- Screenshot Message -->
        <div class="screenshot-note">
          <p>Please take a screenshot of this receipt for your records.</p>
          <p class="small">(Im NOT integerating a mail service for this xd)</p>
        </div>
      </div>

      <footer>
        <button @click="close" class="btn close-receipt">Close</button>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  show: Boolean,
  orderId: [String, Number],
  items: Array,
  total: Number
})

const emit = defineEmits(['close'])

const orderDate = computed(() => {
  return new Date().toLocaleString()
})

const subtotal = computed(() => {
  return props.total 
})

function close() {
  emit('close')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-content {
  background: #181a1b;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 1.5rem;
  position: relative;
}
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
}
.receipt {
  padding: 1rem 0;
}
.order-info {
  background: #1b1e1f;
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
}
.order-info p {
  margin: 0.25rem 0;
}
.items-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1.5rem;
}
.items-table th {
  background: #2c3e50;
  color: white;
  padding: 0.5rem;
  text-align: left;
}
.items-table td {
  padding: 0.5rem;
  border-bottom: 1px solid #ecf0f1;
}
.totals {
  border-top: 2px solid #2c3e50;
  padding-top: 1rem;
  margin-bottom: 1.5rem;
}
.total-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 1rem;
}
.grand-total {
  font-size: 1.2rem;
  font-weight: bold;
  border-top: 1px solid #bdc3c7;
  padding-top: 0.5rem;
  margin-top: 0.5rem;
}
.screenshot-note {
  background: #fff3cd;
  border: 1px solid #ffeeba;
  color: #856404;
  padding: 1rem;
  border-radius: 4px;
  text-align: center;
  font-weight: bold;
}
.screenshot-note .small {
  font-size: 0.85rem;
  font-weight: normal;
  margin-top: 0.25rem;
}
footer {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
}
.close-receipt {
  background: #4caf50;
  color: white;
  padding: 0.5rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>