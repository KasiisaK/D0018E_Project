import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import './style.css'
import App from './App.vue'
import Home from './views/Home.vue'
import About from './views/About.vue'
import Products from './views/Products.vue'
import ProductDetail from './views/ProductDetail.vue'

import Login from './views/Login.vue'      
import Signup from './views/Signup.vue'    

const routes = [
    { path: '/', component: Home },
    { path: '/about', component: About },
    { path: '/products', component: Products },
    { path: '/product/:id', component: ProductDetail },
    // add contacts page 

    // authentication 
    { path: '/login', component: Login },
    { path: '/signup', component: Signup },
]

const router = createRouter({ 
    history: createWebHistory(),
    routes
})

const pinia = createPinia()
const app = createApp(App)
app.use(router)
app.use(pinia)

app.mount('#app')