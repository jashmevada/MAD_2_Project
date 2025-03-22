<template>
  <div class="d-flex">
    <div class="sidebar bg-light" :class="{ 'sidebar-open': isSidebarOpen }">

      <div class="sidebar-header p-3 border-bottom d-flex align-items-center">
        <h4 class="mb-0">Student Portal</h4>
      </div>

      <div class="sidebar-content p-3">
        <div v-for="(item, index) in items" :key="index" class="mb-2">
          <!-- Parent menu item -->
          <div 
            v-if="item.children"
            @click="toggleSubmenu(index)" 
            class="sidebar-item d-flex align-items-center justify-content-between p-2 cursor-pointer"
            :class="{ 'active': isActiveParent(item) }"
          >
            <div class="d-flex align-items-center">
              <Icon :icon="item.icon" class="me-3" width="20" />
              {{ item.title }}
            </div>
            <Icon 
              v-if="item.children" 
              :icon="expandedMenus.includes(index) ? 'heroicons:chevron-down' : 'heroicons:chevron-right'" 
              width="16" 
            />
          </div>

          <BNav v-else vertical class="sidebar-nav">
            <BNavItem :to="item.link" active-class="active" class="sidebar-item">
              <div class="d-flex align-items-center">
                <Icon :icon="item.icon" class="me-3" width="20" />
                {{ item.title }}
              </div>
            </BNavItem>
          </BNav>

          <!-- Submenu items -->
          <BCollapse :visible="expandedMenus.includes(index) && item.children">
            <BNav vertical class="ms-4 mt-1">
              <BNavItem 
                v-for="(child, childIndex) in item.children" 
                :key="childIndex"
                :to="child.link" 
                active-class="active" 
                class="sidebar-subitem py-1"
              >
                <div class="d-flex align-items-center">
                  <Icon :icon="child.icon" class="me-2" width="16" />
                  {{ child.title }}
                </div>
              </BNavItem>
            </BNav>
          </BCollapse>

          <!-- Regular menu item without children -->
          
        </div>

        <div class="mt-4 pt-3 border-top">
          <h6 class="text-muted text-uppercase small fw-bold mb-3">User</h6>
          <div class="d-flex align-items-center mb-3">
            <BAvatar src="https://i.pravatar.cc/150?img=12" size="md" class="me-2"></BAvatar>
            <div>
              <div class="fw-bold">John Doe</div>
              <small class="text-muted">Administrator</small>
            </div>
          </div>
          <BButton variant="outline-danger" size="sm" class="d-flex align-items-center w-100">
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
        <BNavbarBrand :href="$route.path">{{ $route.name }}</BNavbarBrand>

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
import { ref, computed , onMounted} from 'vue'
import { Icon } from '@iconify/vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isSidebarOpen = ref(true)
const expandedMenus = ref([])

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

const toggleSubmenu = (index) => {
  const position = expandedMenus.value.indexOf(index)
  if (position !== -1) {
    expandedMenus.value.splice(position, 1)
  } else {
    expandedMenus.value.push(index)
  }
}

// Check if any child route is active to highlight parent
const isActiveParent = (item) => {
  if (!item.children) return false
  return item.children.some(child => route.path.startsWith(child.link))
}

// Auto-expand menu if a child route is active
const initializeExpandedMenus = () => {
  items.forEach((item, index) => {
    if (item.children && item.children.some(child => route.path.startsWith(child.link))) {
      if (!expandedMenus.value.includes(index)) {
        expandedMenus.value.push(index)
      }
    }
  })
}

// Initialize expanded menus
onMounted(() => {
  initializeExpandedMenus()

})

const items = [
  { 
    title: 'Home', 
    link: '/student/dashboard', 
    icon: 'heroicons:home' 
  },
  { 
    title: 'Subjects', 
    link: '/subjects', 
    icon: 'heroicons:user-group' 
  },
  { 
    title: 'Quizzes', 
    icon: 'heroicons:clipboard',
    children: [
      { title: 'Find Quiz', link: 'quiz/find', icon: 'heroicons:magnifying-glass' },
      { title: 'My Quizzes', link: 'quiz/my-quizzes', icon: 'heroicons:document-text' },
      // { title: 'Create Quiz', link: 'quiz/create', icon: 'heroicons:plus-circle' },
      { title: 'Quiz History', link: 'quiz/history', icon: 'heroicons:clock' }
    ]
  },
]
</script>

<style scoped>
.sidebar {
  width: 240px;
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
  margin-left: 240px;
  width: calc(100% - 240px);
  transition: margin-left 0.3s ease, width 0.3s ease;
  min-height: 100vh;
}

.sidebar:not(.sidebar-open)+.main-content {
  margin-left: 0;
  width: 100%;
}

.sidebar-nav {
  margin-top: 0.5rem;
}

.sidebar-item {
  border-radius: 0.5rem;
  margin-bottom: 0.25rem;
  transition: all 0.2s;
  cursor: pointer;
}

.sidebar-subitem {
  border-radius: 0.5rem;
  transition: all 0.2s;
  font-size: 0.9rem;
}

/* Active item styling */
.nav-item .nav-link.active {
  background-color: #3b82f6 !important;
  color: white !important;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.sidebar-item.active {
  background-color: rgba(59, 130, 246, 0.2);
  font-weight: bold;
}

.sidebar-item:hover:not(.active) {
  background-color: rgba(59, 130, 246, 0.1);
}

.sidebar-subitem:hover:not(.active) {
  background-color: rgba(59, 130, 246, 0.05);
}

.toggle-btn {
  border: none;
  background: transparent;
}

.toggle-btn:hover,
.toggle-btn:focus {
  background-color: rgba(0, 0, 0, 0.05);
}

.cursor-pointer {
  cursor: pointer;
}
</style>
