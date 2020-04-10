<template>
  <div>
     <li>
        <a class="waves-effect collection-item active" href="#!">
             ({{ feature.total_count }}) {{ feature.name}}
          <i class="material-icons"
             :style="[feature.has_broken_xlinks ? {color: '#ee6e73'} : {color: '#26a69a'}]"
             @click="featureSelected">{{ icon }}</i>
        </a>
     </li>
  </div>
</template>

<script>
import EventBus from '../event-bus';

export default {
  name: 'Feature',
  props: ['feature'],
  methods: {
    featureSelected() {
      EventBus.$emit('feature-selected', this.feature);
    },
  },
  computed: {
    icon() {
      return this.feature.has_broken_xlinks ? 'report' : 'done';
    },
  },
};
</script>
