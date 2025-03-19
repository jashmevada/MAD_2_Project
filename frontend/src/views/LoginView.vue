<script setup lang="js">
import { ref } from "vue"
import { useLoginStore } from "@/stores/AuthStore"

const loginStore = useLoginStore()

const email = ref()
const username = ref()
const password = ref()

async function handleLogin(e) {
  console.log(e);
  
  try {
    await loginStore.login(username.value, password.value)
  }
  catch (e) {
    console.log(e);

  }
}

</script>

<template>
  <div class="container d-flex justify-content-center align-items-center vh-100">
    <div class="card shadow">
      <div class="card-header text-center">
        <h3>Login to Quiz App</h3>
      </div>
      <div class="card-body">
        <form @submit.prevent="handleLogin">
          <div class="mb-3">
            <label for="username" class="form-label">Username</label>
            <input
              type="text"
              class="form-control"
              id="username"
              v-model="username"
              required
              placeholder="Enter your username"
            />
          </div>
          <div class="mb-3">
            <label for="password" class="form-label">Password</label>
            <input
              type="password"
              class="form-control"
              id="password"
              v-model="password"
              required
              placeholder="Enter your password"
            />
          </div>
          <button type="submit" class="btn btn-primary w-100">Login</button>
        </form>
        <div class="mt-3 text-center">
          <p>Don't have an account? <router-link to="/register">Register here</router-link></p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  max-width: 400px;
  width: 100%;
}
</style>