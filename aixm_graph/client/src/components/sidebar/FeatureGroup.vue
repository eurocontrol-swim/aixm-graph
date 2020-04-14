<template>
  <div>
     <li @click="featureGroupSelected">
        <a class="waves-effect collection-item active" href="#!" >
             ({{ featureGroup.totalCount }}) {{ featureGroup.name}}
          <i class="material-icons"
             :style="[featureGroup.hasBrokenXlinks ? {color: '#ee6e73'} : {color: '#26a69a'}]">
             {{ icon }}
          </i>
        </a>
     </li>
  </div>
</template>

<script>
import EventBus from '../event-bus';

export default {
  name: 'FeatureGroup',
  props: ['featureGroup', 'datasetId'],
  methods: {
    featureGroupSelected() {
      EventBus.$emit('feature-group-selected', this.datasetId, this.featureGroup.name);
    },
  },
  computed: {
    icon() {
      return this.featureGroup.hasBrokenXlinks ? 'report' : 'done';
    },
  },
};
</script>
