import './assets/main.css'
// import 'bootstrap/dist/css/bootstrap.min.css'
// import './assets/styles.scss'
//import "bootstrap-table"
// import * as bootstrap from 'bootstrap'
// import 'bootstrap'
import { createBootstrap } from 'bootstrap-vue-next'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue-next/dist/bootstrap-vue-next.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { ofetch } from 'ofetch'

import App from './App.vue'
import router from './router'

const app = createApp(App)

export const apiFetch = ofetch.create({ baseURL: `${import.meta.env.VITE_HOST}/api/` })

app.use(createPinia())
app.use(router)
app.use(createBootstrap())

app.mount('#app')
