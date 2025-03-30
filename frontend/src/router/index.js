import { useLoginStore } from '@/stores/AuthStore'
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
      meta: { requiresAuth: true, role: 'admin' },
      beforeEnter: async (to) => {      
        return to.meta.role === 'admin' &&
        localStorage.getItem('role') === 'admin'
          ? true
          : '/'
      },
      component: () => import("@/components/adminLayout.vue"),
      children: [
        { path: 'dashboard', name: "Admin Dashboard", component: () => import("@/views/admin/DashboardView.vue") },
        {
          path: 'instructors',
          children: [
            { path: 'verify', name: "Instructors", component: () => import("@/views/admin/VerfiyInstructorsView.vue") }]
        },
        {
          path: 'departments',
          name: 'Departments',
          component: () => import("@/views/admin/DepartmentsView.vue")
        },
        {
          path: "students",
          name: "Students",
          component: () => import("@/views/admin/StudentsView.vue")
        },
        {
          path: 'students/:id',
          name: "Students Quiz Scores",
          component: () => import("@/views/admin/StudentsQuizView.vue")
        },
        {
          path: 'students/:id/score',
          name: "Student Score",
          component: () => import("@/views/student/QuizScoreView.vue")
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
          name: "Create Quiz",
          path: "quiz/create",
          component: () => import("@/views/QuizCreateView.vue")
        },
        {
          name: "Quiz Detail",
          path: 'quiz/:id/detail',
          component: () => import("@/views/QuizDetailView.vue")
        },
        {
          name: 'Edit Quiz',
          path: 'quiz/:id/edit',
          component: () => import("@/views/QuizEditView.vue")
        },
        {
          path: 'subjects/:id',
          name: 'Admin Subject Detail',
          component: () => import("@/views/admin/SubjectDetailView.vue")
        }
      ]
    },
    {
      name: 'Instructor',
      path: "/instructor",
      beforeEnter: async (to) => {
        return to.meta.role === 'instructor' &&
        localStorage.getItem('role') === 'instructor'
          ? true
          : '/'
      },
      meta: { requiresAuth: true, role: 'instructor' },
      component: () => import("@/components/instructorLayout.vue"),
      children: [
        {
          path: 'dashboard',
          name: "Instructor Dashboard",
          component: () => import("@/views/instructor/DashboardView.vue")
        },
        {
          path: 'chapters',
          name: "Your Subject",
          component: () => import("@/views/instructor/ChaptersView.vue")
        },
        {
          path: 'quiz',
          name: 'Quizzes',
          component: () => import("@/views/instructor/QuizView.vue")
        }, 
        {
          name: "Create New Quiz",
          path: 'quiz/create',
          component: () => import("@/views/QuizCreateView.vue")
        },
        {
          name: 'Quiz Edit',
          path: 'quiz/:id/edit',
          component: () => import("@/views/QuizEditView.vue")
        },
        {
          path: 'subjects/:id',
          name: 'Instructor Subject Detail',
          component: () => import("@/views/admin/SubjectDetailView.vue")
        }
      ]
    },
    {
      name: 'Student',
      path: '/student',
      beforeEnter: async (to) => {
        return to.meta.role === 'student' &&
        localStorage.getItem('role') === 'student'
          ? true
          : '/'
      },
      meta: { requiresAuth: true, role: 'student' },
      component: () => import("@/components/studentLayout.vue"),
      children: [
        {
          name: "Student Dashboard",
          path: 'dashboard',
          component: () => import("@/views/student/DashboardView.vue")
        },
        {
          name: "Find Quiz",
          path: 'quiz/find',
          component: () => import("@/views/student/QuizFindView.vue")
        },
        {
          name: 'Your Accept Quizzes',
          path: 'quiz/my-quizzes',
          component: () => import("@/views/student/QuizView.vue"),
        },
        {
          name: "Quiz Window",
          path: 'quiz/:id/attempt',
          component: () => import("@/views/student/QuizWindow.vue") // QuizAttemptView
        },
        {
          name: "Quiz Scores",
          path: 'quiz/:id/score',
          component: () => import("@/views/student/QuizScoreView.vue"),
         
        }

      ]
    },
  ],
})

router.beforeEach(async (to, from, next) => {
  const loginStore = useLoginStore()
  loginStore.loadToken()
  
  if (
    to.matched.some(rec => rec.meta.requiresAuth) &&
    to.matched.some(rec => rec.meta.role)
  ) {
    if (!loginStore.isAuthenticated()) {
      next({ path: '/' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
