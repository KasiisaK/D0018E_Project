import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import api from '../api/index'


// TODO: add userId param to all functions and call with authStore.user.id once we have auth working. For now we hardcode userId=1

export const useCartStore = defineStore('cart', () => {
  const items = ref([])

  // ===== LOAD CART FROM BACKEND =====
  async function fetchCart(userId = 1) {
    const response = await api.get(`/cart/${userId}`);
    items.value = response.data;
  }

  // ===== ADD ITEM =====
  async function addToCart(productId, quantity = 1, userId = 1) {
    await api.post('/cart/add', {
      user_id: userId,
      product_id: productId,
      quantity
    });
    await fetchCart(userId);
  }

  // ===== UPDATE QUANTITY =====
  async function updateQuantity(productId, quantity, userId = 1) {
    await api.put('/cart/setQuantity', {
      user_id: userId,
      product_id: productId,
      quantity
    });
    await fetchCart(userId);
  }

  // ===== REMOVE =====
  async function removeItem(productId, userId = 1) {
    await api.delete('/cart/remove', {
      data: { user_id: userId, product_id: productId }
    });
    await fetchCart(userId);
  }

  // ===== MAKE ORDER =====
  async function createOrder(userId = 1) {
    const response = await api.post('/orders/create', {
      user_id: userId
    });
    await fetchCart(userId);
    return response.data.order_id;
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
    removeItem,
    createOrder
  }
})