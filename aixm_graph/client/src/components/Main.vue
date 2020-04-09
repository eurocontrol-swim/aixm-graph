<template>
  <div>
    <ul>
      <li v-for="dataset in datasets"
          v-bind:dataset="dataset"
          v-bind:key="dataset.dataset_id">
          {{ dataset.dataset_name }}
      </li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Main',
  data() {
    return {
      datasets: [],
    };
  },
  methods: {
    getMessage() {
      const path = 'http://localhost:3000/load-datasets';
      axios.get(path)
        .then((res) => {
          console.log(res);
          this.datasets = res.data.data;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
  },
  created() {
    this.getMessage();
  },
};
</script>
