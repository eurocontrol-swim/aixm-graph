import Vue from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';

import 'materialize-css/dist/css/materialize.css';

import './assets/css/app.css';
import './assets/css/material_icons.css';

Vue.config.productionTip = false;

new Vue({
  router,
  store,
  render: (h) => h(App),
}).$mount('#app');
