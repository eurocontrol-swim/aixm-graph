<template>
  <div>
    <navbar></navbar>
    <dataset></dataset>
  </div>
</template>

<script>
import M from 'materialize-css';
import Navbar from './navbar/Navbar.vue';
import Dataset from './sidebar/Dataset.vue';

export default {
  name: 'Main',
  components: {
    Navbar,
    Dataset,
  },
  methods: {
    initMateriazeComponents() {
      document.addEventListener('DOMContentLoaded', () => {
        M.Dropdown.init(document.querySelectorAll('.dropdown-trigger'), {});
        M.Modal.init(document.querySelectorAll('.modal'), {});
        M.Sidenav.init(document.querySelectorAll('.sidenav'), {});
        M.Collapsible.init(document.querySelectorAll('.collapsible'), {});
        M.Tooltip.init(document.querySelectorAll('.tooltipped'), {});
      });
    },
  },
  created() {
    this.initMateriazeComponents();
  },
};
</script>
