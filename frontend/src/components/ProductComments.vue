<template>
  <div class="product-comments">
    <h3>Customer Reviews</h3>

    <!-- Loading state -->
    <div v-if="loading" class="comments-loading">Loading reviews...</div>

    <!-- Error state -->
    <div v-else-if="error" class="comments-error">
      {{ error }}
      <button @click="fetchReviews" class="retry-btn">Retry</button>
    </div>

    <!-- Reviews list -->
    <div v-else class="comments-list">
      <div v-if="reviews.length === 0" class="no-comments">
        No reviews yet. Be the first to review this product!
      </div>

      <div
        v-for="review in reviews"
        :key="review.review_id"
        class="comment-item"
        :class="{ 'own-comment': review.isOwn }"
      >
        <div class="comment-header">
          <span class="comment-author">{{ review.user_name }}</span>
          <span class="comment-date">{{ formatDate(review.created_at) }}</span>
        </div>
        <!-- Star display for the review's rating -->
        <div class="review-rating">
          <i v-for="star in review.rating" :key="'full'+star" class="fas fa-star"></i>
          <i v-for="star in (5 - review.rating)" :key="'empty'+star" class="far fa-star"></i>
          <span>({{ review.rating }}/5)</span>
        </div>
        <p class="comment-text">{{ review.comment || '(No comment)' }}</p>

        <!-- If this is the user's own review, show edit/delete buttons -->
        <div v-if="review.isOwn || authStore.user?.isAdmin" class="own-comment-actions">
          <button @click="startEdit(review)" v-if="review.isOwn" class="edit-btn">Edit</button>
          <button @click="deleteReview(review)" class="delete-btn">Delete</button>
        </div>
      </div>
    </div>

    <!-- Review form for logged‑in users (only if they haven't reviewed yet) -->
    <div v-if="authStore.isAuthenticated && !editingReview && !hasUserReviewed" class="comment-form">
      <h4>Write your review</h4>
      <!-- Star rating input -->
      <div class="rating-input">
        <span>Your rating:</span>
        <div class="stars">
          <i
            v-for="star in 5"
            :key="star"
            class="fas fa-star"
            :class="{ 'selected': star <= newRating }"
            @click="newRating = star"
          ></i>
        </div>
      </div>
      <textarea
        v-model="newComment"
        placeholder="Write your comment here (optional)..."
        rows="3"
      ></textarea>
      <button
        @click="submitReview"
        :disabled="newRating === 0 || submitting"
        class="submit-btn"
      >
        {{ submitting ? 'Posting...' : 'Post Review' }}
      </button>
    </div>

    <!-- Edit form (shown when editing) -->
    <div v-else-if="authStore.isAuthenticated && editingReview" class="comment-form edit-form">
      <h4>Edit your review</h4>
      <div class="rating-input">
        <span>Your rating:</span>
        <div class="stars">
          <i
            v-for="star in 5"
            :key="star"
            class="fas fa-star"
            :class="{ 'selected': star <= editRating }"
            @click="editRating = star"
          ></i>
        </div>
      </div>
      <textarea
        v-model="editComment"
        placeholder="Edit your comment..."
        rows="3"
      ></textarea>
      <div class="edit-actions">
        <button @click="updateReview" :disabled="editRating === 0 || submitting" class="update-btn">
          {{ submitting ? 'Updating...' : 'Update' }}
        </button>
        <button @click="cancelEdit" class="cancel-btn">Cancel</button>
      </div>
    </div>

    <!-- Message for non‑logged‑in users -->
    <div v-else-if="!authStore.isAuthenticated" class="login-prompt">
      <router-link to="/login">Log in</router-link> to leave a review.
    </div>

    <!-- If user already reviewed and not editing, optionally show a note (the edit/delete buttons are already visible) -->
    <div v-else-if="authStore.isAuthenticated && hasUserReviewed && !editingReview" class="already-reviewed">
      You have already reviewed this product.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import api from '../api/index'

const props = defineProps({
  productId: {
    type: [String, Number],
    required: true
  }
})

// Emit events to parent so it can refresh product data
const emit = defineEmits(['review-submitted', 'review-updated', 'review-deleted'])

const authStore = useAuthStore()

// State
const reviews = ref([])
const loading = ref(true)
const error = ref(null)
const submitting = ref(false)

// New review fields
const newRating = ref(0)
const newComment = ref('')

// Editing state
const editingReview = ref(null)   // holds the review object being edited
const editRating = ref(0)
const editComment = ref('')

// Computed: has the current user already reviewed?
const hasUserReviewed = computed(() => {
  return reviews.value.some(review => review.isOwn)
})

// Fetch all reviews for this product
const fetchReviews = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await api.get(`/products/${props.productId}/reviews`)
    let fetched = response.data

    // Ensure rating is a number
    fetched = fetched.map(review => ({
      ...review,
      rating: Number(review.rating)  // convert to number
    }))

    // Mark user's own review if logged in
    if (authStore.isAuthenticated) {
      const userId = authStore.user?.id
      reviews.value = fetched.map(review => ({
        ...review,
        isOwn: review.user_id === userId
      }))
    } else {
      reviews.value = fetched.map(review => ({ ...review, isOwn: false }))
    }
  } catch (err) {
    console.error('Failed to fetch reviews:', err)
    error.value = 'Could not load reviews. Please try again.'
  } finally {
    loading.value = false
  }
}

// Format date (simple)
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString() // you can customize
}

// Submit a new review
const submitReview = async () => {
  if (newRating.value === 0) return // rating is required
  submitting.value = true
  try {
    await api.post(`/products/${props.productId}/reviews`, {
      rating: newRating.value,
      comment: newComment.value.trim() || null // send null if empty
    })
    // After successful post, refresh reviews and reset form
    await fetchReviews()
    newRating.value = 0
    newComment.value = ''
    emit('review-submitted')
  } catch (err) {
    console.error('Failed to post review:', err)
    alert('Could not post review. Please try again.')
  } finally {
    submitting.value = false
  }
}

// Start editing a review
const startEdit = (review) => {
  editingReview.value = review
  editRating.value = review.rating
  editComment.value = review.comment || ''
}

// Cancel editing
const cancelEdit = () => {
  editingReview.value = null
  editRating.value = 0
  editComment.value = ''
}

// Update the existing review
const updateReview = async () => {
  if (editRating.value === 0) return
  submitting.value = true
  try {
    await api.put(`/products/${props.productId}/reviews`, {
      rating: editRating.value,
      comment: editComment.value.trim() || null
    })
    await fetchReviews()
    cancelEdit()
    emit('review-updated')
  } catch (err) {
    console.error('Failed to update review:', err)
    alert('Could not update review. Please try again.')
  } finally {
    submitting.value = false
  }
}

// Delete the user's review
const deleteReview = async (review) => {
  if (!confirm('Are you sure you want to delete this review?')) return

  submitting.value = true
  try {
    // If user is admin, use admin endpoint (with review_id)
    if (authStore.user?.isAdmin) {
      await api.delete(`/admin/reviews/${review.review_id}`)
    } else {
      // Otherwise, use the regular user endpoint (deletes own review)
      await api.delete(`/products/${props.productId}/reviews`)
    }
    await fetchReviews()
    emit('review-deleted')
  } catch (err) {
    console.error('Failed to delete review:', err)
    alert('Could not delete review. Please try again.')
  } finally {
    submitting.value = false
  }
}

// Load reviews on mount
onMounted(() => {
  fetchReviews()
})
</script>

<style scoped>
.product-comments {
  margin-top: 3rem;
  border-top: 1px solid #eee;
  padding-top: 2rem;
}
.comments-list {
  margin: 1.5rem 0;
}
.comment-item {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  position: relative;
}
.comment-item.own-comment {
  border-left: 4px solid #4caf50;
}
.comment-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}
.comment-author {
  font-weight: bold;
  color: #333;
}
.comment-date {
  color: #777;
}
.review-rating {
  margin-bottom: 0.5rem;
  color: #f39c12;
}
.review-rating span {
  margin-left: 0.5rem;
  color: #555;
  font-size: 0.9rem;
}
.comment-text {
  margin: 0.5rem 0;
  line-height: 1.5;
  color: black;
}
.own-comment-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}
.own-comment-actions button {
  padding: 0.3rem 0.8rem;
  font-size: 0.8rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.edit-btn {
  background: #ffc107;
  color: #333;
}
.delete-btn {
  background: #dc3545;
  color: white;
}
.comment-form {
  margin-top: 2rem;
}
.rating-input {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}
.rating-input span {
  margin-right: 1rem;
}
.stars {
  display: flex;
  gap: 0.2rem;
}
.stars i {
  font-size: 1.5rem;
  color: #ddd;
  cursor: pointer;
  transition: color 0.2s;
}
.stars i.selected {
  color: #f39c12;
}
.comment-form textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  resize: vertical;
  margin-bottom: 0.5rem;
}
.comment-form button {
  padding: 0.6rem 1.5rem;
  border: none;
  border-radius: 4px;
  background: #4caf50;
  color: white;
  font-weight: bold;
  cursor: pointer;
}
.comment-form button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
.edit-form {
  background: #fff3cd;
  padding: 1rem;
  border-radius: 8px;
}
.edit-actions {
  display: flex;
  gap: 0.5rem;
}
.update-btn {
  background: #28a745;
}
.cancel-btn {
  background: #6c757d;
}
.login-prompt, .already-reviewed {
  margin-top: 1.5rem;
  padding: 1rem;
  background: #f1f1f1;
  border-radius: 4px;
  text-align: center;
  color: black;
}
.no-comments {
  color: #777;
  font-style: italic;
  text-align: center;
  padding: 2rem;
}
</style>