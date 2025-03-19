import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import("@/views/LoginView.vue"),
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: "/test",
      component: () => import("@/components/test.vue")
    },
    {
      path: "/register",
      name: "register",
      component: () => import("@/views/RegisterView.vue"),
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import("@/components/adminLayout.vue"),
      children: [
        { path: 'dashboard', name: "Dashboard", component: () => import("@/views/admin/DashboardView.vue") },
        {
          path: 'instructors',
          children: [
            { path: 'verify', component: () => import("@/views/admin/VerfiyInstructorsView.vue") }]
        },
        {
          path: 'subjects',
          name: 'Subjects Management',
          component: () => import("@/views/admin/SubjectsView.vue"),
          children: [
            { path: 'add', component: () => import("@/views/admin/SubjectsAddView.vue") }
          ]
        },
        {
          path: 'subjects/:id',
          name: 'Subject Detail',
          component: () => import("@/views/admin/SubjectDetailView.vue")
        }

      ]
    },
    {
      name: 'instructor',
      path: "/instructor",
      component: () => import("@/components/instructorLayout.vue")
    },
    {
      name: 'student',
      path: '/student',

    }
  ],
})

export default router
