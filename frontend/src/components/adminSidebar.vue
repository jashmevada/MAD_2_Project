<template>
  <div class="d-flex">
    <!-- Sidebar -->
    <div class="sidebar bg-light" :class="{ 'sidebar-open': isSidebarOpen }">
      <div class="sidebar-header p-3 border-bottom d-flex align-items-center">
        <!-- <Icon icon="logos:vue" class="me-2" width="24" /> -->
        <h4 class="mb-0">Admin Potral</h4>
      </div>
      <div class="sidebar-content p-3">
        <BNav vertical class="sidebar-nav">
          <BNavItem to="/admin/dashboard" active-class="active" class="sidebar-item">
            <div class="d-flex align-items-center">
              <Icon icon="heroicons:home" class="me-3" width="20" />
              Dashboard
            </div>
          </BNavItem>

          <BNavItem to="/admin/instructors/verify" active-class="active" class="sidebar-item">
            <div class="d-flex align-items-center">
              <Icon icon="heroicons:chat-bubble-left-right" class="me-3" width="20" />
              Instructors
              <!-- <BBadge variant="danger" class="ms-2">5</BBadge> -->
            </div>
          </BNavItem>


          <BNavItem to="/students" active-class="active" class="sidebar-item">
            <div class="d-flex align-items-center">
              <Icon icon="heroicons:user-group" class="me-3" width="20" />
              Students
            </div>
          </BNavItem>



          <BNavItem to="/admin/subjects" active-class="active" class="sidebar-item">
            <div class="d-flex align-items-center">
              <Icon icon="heroicons:book-open" class="me-3" width="20" />
              Subjects
            </div>
          </BNavItem>


          <BNavItem to="/quiz" active-class="active" class="sidebar-item">
            <div class="d-flex align-items-center">
              <Icon icon="heroicons:clipboard" class="me-3" width="20" />
              Quiz
            </div>
          </BNavItem>

          <router-link to="/analytics" custom v-slot="{ navigate, isActive }">
            <BNavItem @click="navigate" :active="isActive" class="sidebar-item">
              <div class="d-flex align-items-center">
                <Icon icon="heroicons:chart-bar" class="me-3" width="20" />
                Analytics
              </div>
            </BNavItem>
          </router-link>

          <router-link to="/settings" custom v-slot="{ navigate, isActive }">
            <BNavItem @click="navigate" :active="isActive" class="sidebar-item">
              <div class="d-flex align-items-center">
                <Icon icon="heroicons:cog-6-tooth" class="me-3" width="20" />
                Settings
              </div>
            </BNavItem>
          </router-link>
        </BNav>

        <div class="mt-4 pt-3 border-top">
          <h6 class="text-muted text-uppercase small fw-bold mb-3">User</h6>
          <div class="d-flex align-items-center mb-3">
            <BAvatar src="https://i.pravatar.cc/150?img=12" size="md" class="me-2"></BAvatar>
            <div>
              <div class="fw-bold">John Doe</div>
              <small class="text-muted">Administrator</small>
            </div>
          </div>
          <BButton to='/' variant="outline-danger" size="sm" class="d-flex align-items-center w-100">
            <Icon icon="heroicons:arrow-right-on-rectangle" class="me-2" width="16" />
            Logout
          </BButton>
        </div>
      </div>
    </div>

    <!-- Main content -->
    <div class="main-content">
      <BNavbar toggleable variant="light" class="border-bottom">
        <BButton variant="outline-primary" class="me-2 toggle-btn" @click="toggleSidebar">
          <Icon :icon="isSidebarOpen ? 'heroicons:bars-3-bottom-left' : 'heroicons:bars-3'" width="20" />
        </BButton>
        <BNavbarBrand href="#">{{ $route.name }}</BNavbarBrand>

        <div class="ms-auto d-flex align-items-center">
          <BButton variant="light" class="me-2">
            <Icon icon="heroicons:bell" width="20" />
          </BButton>
          <BButton variant="light">
            <Icon icon="heroicons:envelope" width="20" />
          </BButton>
        </div>
      </BNavbar>

      <div class="content p-4">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { BNav, BNavItem, BNavbar, BNavbarBrand, BButton, BAvatar, BBadge } from 'bootstrap-vue-next'
import { Icon } from '@iconify/vue'

const isSidebarOpen = ref(true)

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

const items = [
  { title: 'home', link: '', icon: '' }
]



</script>

<style scoped>
.sidebar {
  width: 280px;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  transition: transform 0.3s ease;
  z-index: 1000;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
}

.sidebar-open {
  transform: translateX(0);
}

.sidebar:not(.sidebar-open) {
  transform: translateX(-100%);
}

.main-content {
  margin-left: 280px;
  width: calc(100% - 280px);
  transition: margin-left 0.3s ease, width 0.3s ease;
  min-height: 100vh;
}

.sidebar:not(.sidebar-open)+.main-content {
  margin-left: 0;
  width: 100%;
}

.sidebar-nav {
  margin-top: 1rem;
}

.sidebar-item {
  border-radius: 0.5rem;
  margin-bottom: 0.25rem;
  transition: all 0.2s;
}

/* Active item styling */
.nav-item .nav-link.active {
  background-color: #3b82f6 !important;
  color: white !important;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}



.sidebar-item:hover:not(.active) {
  background-color: rgba(59, 130, 246, 0.1);
}

.toggle-btn {
  border: none;
  background: transparent;
}

.toggle-btn:hover,
.toggle-btn:focus {
  background-color: rgba(0, 0, 0, 0.05);
}
</style>
