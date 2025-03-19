import { defineStore } from 'pinia'

export const useRouteStore = defineStore('routeStore', {
  state: () => ({
    currentRoute: null,
  }),
  actions: {
    setCurrentRoute(route) {
      this.currentRoute = route
      // sessionStorage.setItem('currentRoute', route)
    },
    getCurrentRoute() {
      return this.currentRoute
      // return sessionStorage.getItem('currentRoute')
    },
  },
})
