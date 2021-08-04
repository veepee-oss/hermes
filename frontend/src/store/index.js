import config from '../config.json'

import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

// config['api_url'] can accept http://hostname:port or :port
// check the relevant case here

let api_url_used = config['api_url'];
if (/:[0-9]*$/.test(api_url_used) == true){
  api_url_used = location.protocol + '//' + location.hostname + ':' + api_url_used.replace(':','');
}


let axios = require('axios').create({
    baseURL: api_url_used,
    timeout: config['api_default_timeout'],
});

let store = new Vuex.Store({
  state: {
    token: localStorage.getItem('access_token') || null,
    token_creation_time: localStorage.getItem('access_token_date') || null,
    user_id: localStorage.getItem('user_id') || null,
  },
  getters: {
    loggedIn(state){
      return state.token !== null;
    },

    fetchStoredToken(state){
      return state.token;
    }
  },
  mutations: {
    retreiveToken(state, token_response){
      state.token = token_response.token;
      state.date = token_response.date;
    },
    destroyToken(state){
      state.token = null;
      state.token_creation_time = null;
    }
  },
  actions: {
    retreiveToken(context, credentials){
      return new Promise((resolve, reject) => {
        axios.get('/auth/get_token',{
            headers: {
                Authorization: 'Basic ' + btoa(credentials.email_username + ':' + credentials.password)
            }
          })
          .then(response =>{
            if (response.status === 200){
              let register_date = Math.floor(Date.now() / 1000);
              localStorage.setItem('access_token', response.data.token);
              localStorage.setItem('access_token_date', register_date);
              context.commit('retreiveToken', {token: response.data.token, date: register_date});
              resolve(response.data);
            }else{
              reject(String("Error during Authorization"));
            }
            
          })
          .catch(error =>{
            reject(String("Not Authorized , error is : " + String(error)));
          });
      });
    },
    destroyToken(context){
      localStorage.removeItem('access_token');
      localStorage.removeItem('access_token_date');
      context.commit('destroyToken');
    }
  },
});

Vue.set(store, 'axios_obj', axios);

export let StoreAxios = {
    axios: axios,
    store: store
}
