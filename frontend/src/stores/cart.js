import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'


// TODO: add userId param to all functions and call with authStore.user.id once we have auth working. For now we hardcode userId=1

export const useCartStore = defineStore('cart', () => {
  const items = ref([])

  // ===== LOAD CART FROM BACKEND =====
  async function fetchCart(userId = 1) {
    const response = await axios.get(`http://127.0.0.1:5000/cart/${userId}`)
    items.value = response.data
  }

  // ===== ADD ITEM =====
  async function addToCart(productId, quantity = 1, userId = 1) {
    await axios.post('http://127.0.0.1:5000/cart/add', {
      user_id: userId,
      product_id: productId,
      quantity
    })

    await fetchCart(userId) // refresh local state
  }

  // ===== UPDATE QUANTITY =====
  async function updateQuantity(productId, quantity, userId = 1) {
    await axios.put('http://127.0.0.1:5000/cart/setQuantity', {
      user_id: userId,
      product_id: productId,
      quantity
    })

    await fetchCart(userId)
  }

  // ===== REMOVE =====
  async function removeItem(productId, userId = 1) {
    await axios.delete('http://127.0.0.1:5000/cart/remove', {
      data: { user_id: userId, product_id: productId }
    })

    await fetchCart(userId)
  }

  // ===== GETTERS =====
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
    removeItem
  }
})