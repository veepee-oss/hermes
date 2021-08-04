import Vue from 'vue'

import Router from 'vue-router'
Vue.use(Router);

import lander from '../pages/lander.vue'
import login from '../pages/login.vue'
import editConf from '../pages/editConf.vue'
import editSite from '../pages/editSite.vue'

export default new Router({
    scrollBehavior() {
        return window.scrollTo({ top: 0, behavior: 'smooth' });
    },
    mode: 'history',
    routes: [

        // Dashboards

        {
            path: '/',
            name: 'lander',
            meta: {requiresAuth: true},
            component: lander,
        },

        {
            path: '/editconfig',
            name: 'editconfig',
            meta: {requiresAuth: true},
            component: editConf
        },

        {
            path: '/editsite',
            name: 'editsite',
            meta: {requiresAuth: true},
            component: editSite
        },

        // Pages

        {
            path: '/login',
            name: 'login-boxed',
            meta: {layout: 'userpages'},
            component: login,
        }
    ]
})
