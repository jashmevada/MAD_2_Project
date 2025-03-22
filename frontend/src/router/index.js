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
        { path: 'dashboard', name: "Admin Dashboard", component: () => import("@/views/admin/DashboardView.vue") },
        {
          path: 'instructors',
          children: [
            { path: 'verify', name: "Instructors", component: () => import("@/views/admin/VerfiyInstructorsView.vue") }]
        },
        {
          path: "students",
          name: "Students",
          component: () => import("@/views/admin/StudentsView.vue")
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
          path: 'quiz',
          name: 'Quiz Management',
          component: () => import("@/views/admin/QuizView.vue"),
        },
        {
          name: "Create New Quiz",
          path: 'quiz/create',
          component: () => import("@/views/QuizCreateView.vue")
        },
        {
          name: "Quiz Detail",
          path: 'quiz/detail',
          component: () => import("@/views/QuizDetailView.vue")
        },
        {
          name: 'Edit Quiz',
          path: 'quiz/edit',
          component: () => import("@/views/QuizEditView.vue")
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
      component: () => import("@/components/instructorLayout.vue"),
      children: [
        // {
        //   path: '/dashboard',
        //   name: "Instructor Dashboard",
        //   component: () => import("@/views/instructor/DashboardView.vue")
        // },
        // {
        //   path: '/subjects',
        //   name: "Subjects",
        //   component: () => import("@/views/instructor/SubjectsView.vue")
        // },
        // {
        //   path: '/subjects/:id',
        //   name: "Subject Detail",
        //   component: () => import("@/views/admin/SubjectDetailView.vue")
        // }
      ]
    },
    {
      name: 'Student',
      path: '/student',
      component: () => import("@/components/studentLayout.vue"),
      children: [
        {
          name: "Student Dashboard",
          path: 'dashboard',
          component: () => import("@/views/student/DashboardView.vue")
        },
        {
          name: 'Quiz',
          path: 'quiz',
          component: () => import("@/views/student/QuizView.vue")
        },
        {
          name: "Find Quiz",
          path: 'quiz/find',
          component: () => import("@/views/student/QuizFindView.vue")
        }
      ]
    }
  ],
})

export default router
