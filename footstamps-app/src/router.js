import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import SearchPane from './components/SearchPane.vue'
import MapPane from './components/MapPane.vue'

Vue.component('search-pane', SearchPane)
Vue.component('map-pane', MapPane)
Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    }
  ]
})
