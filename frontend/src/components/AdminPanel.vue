<template>
  <div v-if="show" class="modal-overlay" @click.self="close">
    <div class="modal-content">
      <header>
        <h2>Admin Panel</h2>
        <button @click="close" class="close-btn">&times;</button>
      </header>

      <!-- Tabs (optional) -->
      <div class="tabs">
        <button :class="{ active: activeTab === 'add' }" @click="activeTab = 'add'">Add Product</button>
        <button :class="{ active: activeTab === 'manage' }" @click="activeTab = 'manage'">Manage Products</button>
      </div>

      <!-- Add Product Tab -->
      <div v-if="activeTab === 'add'" class="tab-content">
        <form @submit.prevent="addProduct">
          <div class="form-group">
            <label>Name *</label>
            <input v-model="newProduct.name" required />
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="newProduct.description"></textarea>
          </div>
          <div class="form-group">
            <label>Price *</label>
            <input type="number" step="0.01" v-model="newProduct.price" required />
          </div>
          <div class="form-group">
            <label>Stock Quantity *</label>
            <input type="number" v-model="newProduct.stock_quantity" required />
          </div>
          <div class="form-group">
            <label>Image URL</label>
            <input v-model="newProduct.image_url" />
          </div>
          <div class="form-group checkbox">
            <label>
              <input type="checkbox" v-model="newProduct.is_best_seller" />
              Best Seller
            </label>
          </div>
          <button type="submit" :disabled="adding">{{ adding ? 'Adding...' : 'Add Product' }}</button>
        </form>
      </div>

      <!-- Manage Products Tab -->
      <div v-if="activeTab === 'manage'" class="tab-content">
        <div v-if="loading" class="loading">Loading products...</div>
        <div v-else-if="error" class="error">{{ error }}</div>
        <table v-else class="product-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Price</th>
              <th>Stock</th>
              <th>Best Seller</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="product in products" :key="product.product_id">
              <td>{{ product.product_id }}</td>
              <td>{{ product.name }}</td>
              <td>${{ product.price }}</td>
              <td>
                <input type="number" v-model.number="product.stock_quantity" @change="updateStock(product)" />
              </td>
              <td>
                <input type="checkbox" :checked="product.is_best_seller" @change="toggleBestSeller(product)" />
              </td>
              <td>
                <button @click="deleteProduct(product)" class="delete-btn">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import api from '../api'

const props = defineProps({
  show: Boolean
})
const emit = defineEmits(['close'])

// Tabs
const activeTab = ref('add')

// Add product form
const newProduct = ref({
  name: '',
  description: '',
  price: null,
  stock_quantity: null,
  image_url: '',
  is_best_seller: false
})
const adding = ref(false)

// Manage products
const products = ref([])
const loading = ref(false)
const error = ref(null)

// Fetch all products when the manage tab is activated
onMounted(() => {
  if (props.show && activeTab.value === 'manage') {
    loadProducts()
  }
})

// Watch for tab changes
watch(activeTab, (newTab) => {
  if (newTab === 'manage') {
    loadProducts()
  }
})

async function loadProducts() {
  loading.value = true
  error.value = null
  try {
    const response = await api.get('/products')
    products.value = response.data
  } catch (err) {
    console.error('Failed to load products', err)
    error.value = 'Could not load products.'
  } finally {
    loading.value = false
  }
}

async function addProduct() {
  adding.value = true
  try {
    await api.post('/admin/products/add', newProduct.value)
    alert('Product added successfully')
    // Reset form
    newProduct.value = {
      name: '',
      description: '',
      price: null,
      stock_quantity: null,
      image_url: '',
      is_best_seller: false
    }
    // If on manage tab, refresh list
    if (activeTab.value === 'manage') {
      await loadProducts()
    }
  } catch (err) {
    console.error('Add product failed', err)
    alert('Failed to add product.')
  } finally {
    adding.value = false
  }
}

async function updateStock(product) {
  try {
    await api.put('/products/quantity', {
      product_id: product.product_id,
      new_quantity: product.stock_quantity
    })
    // No need to reload, just show success optionally
  } catch (err) {
    console.error('Stock update failed', err)
    alert('Could not update stock.')
    // Revert to previous value? For simplicity, reload products
    await loadProducts()
  }
}

async function toggleBestSeller(product) {
  const newValue = !product.is_best_seller
  try {
    await api.patch(`/admin/products/${product.product_id}/best-seller`, {
      is_best_seller: newValue
    })
    product.is_best_seller = newValue // update locally
  } catch (err) {
    console.error('Toggle best seller failed', err)
    alert('Could not update best seller status.')
  }
}

async function deleteProduct(product) {
  if (!confirm(`Are you sure you want to delete "${product.name}"?`)) return
  try {
    await api.delete(`/admin/deleteproducts/${product.product_id}`)
    // Remove from local list
    products.value = products.value.filter(p => p.product_id !== product.product_id)
  } catch (err) {
    console.error('Delete failed', err)
    alert('Could not delete product.')
  }
}

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
  max-width: 1000px;
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
.tabs {
  display: flex;
  gap: 0.5rem;
  border-bottom: 1px solid #ddd;
  margin-bottom: 1rem;
}
.tabs button {
  color: white;
  padding: 0.5rem 1rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
}
.tabs button.active {
  border-bottom-color: #4caf50;
  font-weight: bold;
}
.tab-content {
  padding: 1rem 0;
}
.form-group {
  margin-bottom: 1rem;
}
.form-group label {
  display: block;
  font-weight: bold;
  margin-bottom: 0.25rem;
}
.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #575569;
  border-radius: 4px;
  background-color: #2b2a33;
  color: white;
}
.form-group.checkbox input[type="checkbox"] {
  width: auto;
  margin-right: 0.5rem; 
  background-color: transparent; 
}
.form-group.checkbox {
  display: flex;
  align-items: center;
  margin-top: 0.5rem;
}
button[type="submit"] {
  background: #4caf50;
  color: white;
  padding: 0.5rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
button[type="submit"]:disabled {
  background: #ccc;
  cursor: not-allowed;
}
.product-table {
  width: 100%;
  border-collapse: collapse;
}
.product-table th,
.product-table td {
  border: 1px solid #ddd;
  padding: 0.5rem;
  text-align: left;
}
.product-table th {
  background: #5b8697;
}
.product-table input[type="number"] {
  width: 80px;
}
.delete-btn {
  background: #dc3545;
  color: white;
  border: none;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
}
.loading, .error {
  padding: 2rem;
  text-align: center;
}
</style>