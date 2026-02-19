<template>
  <div>
    <!-- Page Header -->
    <div class="container" style="padding: 40px 20px 20px;">
      <h1 class="section-title">All Mugs</h1>
      <p style="text-align: center; color: #7f8c8d; margin-bottom: 30px;">
        Browse our collection of handcrafted mugs
      </p>
    </div>

    <!-- Products Grid -->
    <section class="products">
      <div class="container">
        <div class="product-grid">
          <div 
            v-for="product in products" 
            :key="product.product_id" 
            class="product-card" 
            @click="goToProduct(product.product_id)"
          >
            <img :src="product.image_url" :alt="product.name" class="product-image">
            <h3 class="product-name">{{ product.name }}</h3>
            <p class="product-price">${{ product.price}}</p>
            <!-- Add .stop to prevent the card's click event from firing -->
            <button class="add-to-cart" @click.stop="addToCart(product)">Add to Cart</button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      products: []  // Initialize products as an empty list
    }
  },
  async created() {
    const response = await axios.get('http://127.0.0.1:5000/products');  // Load the data from your api url
    this.products = response.data;  // set the data
  },
  methods: {
    addToCart(product) {
      axios.post('http://127.0.0.1:5000/cart/add', {
        user_id: 1, // hardcoded for now as use_id = 1
        product_id: product.product_id,
        quantity: 1
      })
      .catch(error => {
        console.error(error)
      })
    }
  }
}
</script>