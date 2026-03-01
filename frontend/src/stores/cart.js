import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api/index'

export const useCartStore = defineStore('cart', () => {
  const items = ref([])
  const allProducts = ref([]) // Cache of all products for stock checks

  // Load products once (called automatically when needed)
  async function loadProductsIfNeeded() {
    if (allProducts.value.length === 0) {
      try {
        const res = await api.get('/products')
        allProducts.value = res.data
        console.log('Products loaded for stock validation:', allProducts.value.length)
      } catch (err) {
        console.error('Failed to load products for stock check:', err)
      }
    }
  }

  // ===== LOAD CART =====
  async function fetchCart() {
    try {
      const response = await api.get('/cart')
      items.value = response.data
      console.log('Cart fetched:', items.value)
    } catch (err) {
      console.error('Failed to fetch cart:', err)
      items.value = []
    }
  }

  // ===== ADD ITEM (with stock limit check) =====
  async function addToCart(productId, quantity = 1) {
    console.log('addToCart called:', { productId, quantity })

    // Ensure we have product data
    await loadProductsIfNeeded()

    const product = allProducts.value.find(p => p.product_id === productId)
    // Find current quantity in cart
    const currentItem = items.value.find(i => i.product_id === productId)
    const currentQty = currentItem ? currentItem.quantity : 0

    const newTotal = currentQty + quantity

    // Check if new total exceeds stock
    if (newTotal > product.stock_quantity) {
      const allowedAdd = product.stock_quantity - currentQty
      if (allowedAdd <= 0) {
        alert(`Cannot add more — only ${product.stock_quantity} in stock!`)
        return  // don't send request
      }
      quantity = allowedAdd
      alert(`Adding only ${quantity} more (limited by stock of ${product.stock_quantity})`)
    }

    // Send the (possibly reduced) request
    try {
      await api.post('/cart/add', {
        product_id: productId,
        quantity
      })
      await fetchCart()
    } catch (err) {
      console.error('Add to cart failed:', err)
      alert('Failed to add to cart, make sure you are logged in and try again')
    }
  }

  // ===== UPDATE QUANTITY (also cap at stock) =====
  async function updateQuantity(productId, quantity) {
    console.log('updateQuantity called:', { productId, quantity })

    // Ensure we have product data (stock_quantity)
    await loadProductsIfNeeded()

    // Get product to check stock
    const product = allProducts.value.find(p => p.product_id === productId)

    // Cap quantity at stock limit
    if (product && quantity > product.stock_quantity) {
      quantity = product.stock_quantity
      alert(`Quantity capped at ${quantity} (stock limit)`)
    }

    try {
      await api.put('/cart/setQuantity', {
        product_id: productId,
        quantity
      })
      await fetchCart()
    // Error for debugging
    } catch (err) {
      console.error('Update quantity failed:', err)
      alert('Failed to update quantity')
    }
  }

  // ===== REMOVE =====
  async function removeItem(productId) {
    console.log('Removing item from cart:', productId)
    try {
      await api.delete('/cart/remove', {
        data: { product_id: productId }
      })
      await fetchCart()
    } catch (err) {
      console.error('Remove failed:', err)
      alert('Failed to remove item')
    }
  }

  // ===== CREATE ORDER =====
  async function createOrder() {
    try {
      const response = await api.post('/orders/create')
      await fetchCart()
      return response.data.order_id
    } catch (err) {
      console.error('Create order failed:', err)
      throw err
    }
  }

  // Getters
  const totalItems = computed(() =>
    items.value.reduce((sum, item) => sum + item.quantity, 0)
  )
  const totalTypes = computed(() => items.value.length)
  const totalPrice = computed(() =>
    items.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
  )

  return {
    items,
    totalItems,
    totalTypes,
    totalPrice,
    fetchCart,
    addToCart,
    updateQuantity,
    removeItem,
    createOrder
  }
})