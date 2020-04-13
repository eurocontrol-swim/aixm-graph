<template>
  <div>
    <a class="dropdown-trigger" href="#!" data-target="dropdown-aixm-datasets">
      {{ title }}<i class="material-icons right">arrow_drop_down</i>
    </a>

    <ul id="dropdown-aixm-datasets" class="dropdown-content">
      <li v-for="dataset in datasets"
          :dataset="dataset"
          :key="dataset.id"
          @click="datasetSelected(dataset)">

        <a href="#">{{ dataset.name }}</a>
      </li>
    </ul>

  </div>
</template>
<script>
import EventBus from '../event-bus';

export default {

  name: 'DatasetsList',
  props: ['datasets'],
  methods: {
    datasetSelected(dataset) {
      EventBus.$emit('dataset-selected', dataset);
    },
  },
  computed: {
    title() {
      return this.datasets.length > 0 ? `(${this.datasets.length}) Datasets` : 'No datasets yet...';
    },
  },
};
</script>
