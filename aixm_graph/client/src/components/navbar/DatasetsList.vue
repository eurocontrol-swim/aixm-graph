<template>
  <div>
    <a class="dropdown-trigger" href="#!" data-target="dropdown-aixm-datasets">
      AIXM Datasets<i class="material-icons right">arrow_drop_down</i>
    </a>

    <ul id="dropdown-aixm-datasets" class="dropdown-content">
      <li v-for="dataset in datasets"
          :dataset="dataset"
          :key="dataset.dataset_id"
          v-on:click="loadDataset(dataset)">

        <a href="#">{{ dataset.dataset_name }}</a>
      </li>
    </ul>

  </div>
</template>
<script>
export default {
  name: 'DatasetsList',
  props: ['datasets'],
};
</script>
