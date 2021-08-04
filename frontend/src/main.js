import Vue from 'vue'

import router from './router'
import { StoreAxios } from './store'

// --------------------------------
// Check auth before each call !
router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!StoreAxios.store.getters.loggedIn) {
      next({
        path: '/login',
      })
    } else {
      next()
    }
  } else {
    next()
  }
})

// --------------------------------
// -- Handle 401 responses
StoreAxios.axios.interceptors.response.use(function (response) {
  return response;
},function (error) {
  if ((error !== undefined) && (error.response !== undefined) && (error.response.status === 401) && (error.response.config.url !== '/auth/get_token')) {
    StoreAxios.store.dispatch('destroyToken')
    router.push('/login')
    return Promise.reject('Expired Authentication session.')
  }else{
    return Promise.reject(error)
  }
})



import BootstrapVue from "bootstrap-vue"

import App from './App'

import Default from './Layout/Wrappers/baseLayout.vue';
import Pages from './Layout/Wrappers/pagesLayout.vue';

import Toasted from 'vue-toasted';


Vue.config.productionTip = false;

Vue.use(BootstrapVue);
Vue.use(Toasted);

Vue.component('default-layout', Default);
Vue.component('userpages-layout', Pages);

new Vue({
  el: '#app',
  router,
  template: '<App/>',
  components: { App },
  store: StoreAxios.store
});
