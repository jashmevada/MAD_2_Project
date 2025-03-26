import { ofetch } from 'ofetch'

export const apiFetch = ofetch.create({ 
    baseURL: `${import.meta.env.VITE_HOST}/api`,
    credentials: 'include', 
    async onRequest({ options }) {
        const token = localStorage.getItem('token')
        if (token) {
          options.headers = {
            ...options.headers,
            'Authorization': `Bearer ${token}`
          }
        }
      }
})
