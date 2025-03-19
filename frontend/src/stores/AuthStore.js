import { defineStore } from 'pinia'
import { ofetch } from 'ofetch'
import router from '@/router/index.js'
import Cookies from 'universal-cookie'

const cookies = new Cookies(null, { path: '/' })

export const useLoginStore = defineStore('login', {
    state: () => ({
        token: null,
        role: null,
        user: null,
    }),
    actions: {
        async login(email, password) {
            // http://${import.meta.env.VITE_HOST}:5000/api/login
            const response = await ofetch(`${import.meta.env.VITE_HOST}/api/login`, {
                method: 'POST',
                body: { username: email, password: password },
                async onResponseError({ response }) {
                    throw response
                },
            })

            this.token = response.access_token
            this.role = response.role
            this.user = response.data

            if (this.token !== '') {
                localStorage.setItem('token', this.token) // Save token to localStorage
                localStorage.setItem('role', this.role)
                sessionStorage.setItem('user', this.user)

                if (cookies.get('user')?.id !== this.user.id) {
                    cookies.set('user', this.user, { secure: true })
                }

                if (this.role === "student") {
                    router.push('/student' || '/') // employee/task
                } else if (this.role === 'instructor') {
                    router.push("/instructor" || '/')
                } else {
                    router.push('/admin/dashboard' || '/')
                }
            }
        },
        logout() {
            this.token = null
            localStorage.removeItem('token')
            localStorage.removeItem('currentRoute')
            localStorage.removeItem('id')
            cookies.remove('user')
            router.push('/')
        },
        loadToken() {
            this.token = localStorage.getItem('token')
        },
        isAuthenticated() {
            this.loadToken()
            return !!this.token
        },
        get_user_data() {
            return cookies.get('user')
        },
    },
})