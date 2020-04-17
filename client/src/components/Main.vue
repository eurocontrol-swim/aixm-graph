<template>
  <div id=main>
    <navbar></navbar>
    <dataset></dataset>
    <graph></graph>
  </div>
</template>

<script>
import M from 'materialize-css';
import Navbar from './navbar/Navbar.vue';
import Dataset from './sidebar/Dataset.vue';
import Graph from './graph/Graph.vue';


export default {
  name: 'Main',
  components: {
    Navbar,
    Dataset,
    Graph,
  },
  methods: {
    initMateriazeComponents() {
      document.addEventListener('DOMContentLoaded', () => {
        M.Dropdown.init(document.querySelectorAll('.dropdown-trigger'), {});
        M.Modal.init(document.querySelectorAll('.modal'), {});
        M.Sidenav.init(document.querySelectorAll('.sidenav'), {});
        M.Collapsible.init(document.querySelectorAll('.collapsible'), {});
        M.Tooltip.init(document.querySelectorAll('.tooltipped'), {});
        M.FormSelect.init(document.querySelectorAll('select'), {});
      });
    },
  },
  created() {
    this.initMateriazeComponents();
  },
};
</script>

<style>

#main {
  height: 100%;
}
</style>
