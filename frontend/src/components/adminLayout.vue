<script setup>
import { ref } from "vue"
import adminSidebar from "./adminSidebar.vue";

const isSidebarCollapsed = ref()


</script>


<template>
  <div class="admin-layout">
    <adminSidebar />
    <!-- <div class="content-wrapper" :class="{ 'content-expanded': isSidebarCollapsed }"> -->
    <!--   <div class="content-container"> -->
    <!--     <router-view /> -->
    <!--   </div> -->
    <!-- </div> -->
  </div>
</template>


<style scoped>
.admin-layout {
  /* display: flex; */
  min-height: 100vh;
}

.content-wrapper {
  flex-grow: 1;
  margin-left: 250px;
  transition: margin 0.3s ease;
  background-color: #f8f9fa;
}

.content-expanded {
  margin-left: 70px;
}

.content-container {
  padding: 20px;
}
</style>
