<template>

  <div class="row" id="side-nav">

    <ul id="slide-out" class="sidenav sidenav-fixed" ref="sidenavList">
      <li class="hide" ref="progress">
      </li>
      <li ref="progressBar" class="hide">
        <div class="progress"><div class="indeterminate"></div></div>
      </li>
      <li class="no-padding">
        <ul class="collapsible collapsible-accordion">
          <li>
            <a class="collapsible-header">
              Dataset: {{ dataset.dataset_name }}<i class="material-icons">arrow_drop_down</i>
            </a>
            <div class="collapsible-body">
              <ul>
              <li>
                <a v-bind:href="skeletonDownloadLink" target="_blank" ref="skeleton">
                  <i class="material-icons">{{ skeletonDownloadIcon }}</i>
                  {{ skeletonDownloadDescription }}
                </a>
              </li>
              <li><div class="divider"></div></li>
              </ul>
            </div>
          </li>
        </ul>
      </li>
      <li class="no-padding">
        <ul class="collapsible collapsible-accordion">
          <li>
            <a class="collapsible-header" ref="featuresTitle">
              {{ featuresDescription }}<i class="material-icons">arrow_drop_down</i>
            </a>
            <div class="collapsible-body">
              <ul>
                <li>
                  <a href="#">
                    <div class="switch">
                      <label>
                        All
                        <input type="checkbox" v-model="brokenFeaturesChecked">
                        <span class="lever"></span>
                        Only with broken links
                      </label>
                    </div>
                  </a>
                </li>
                <li><div class="divider"></div>
                </li>
              </ul>
            </div>
          </li>
        </ul>
      </li>
      <feature v-for="feature in displayableFeatures"
               :feature="feature"
               :key="feature.name">
      </feature>
    </ul>
  </div>

</template>

<script>
import axios from 'axios';
import EventBus from '../event-bus';
import Feature from './Feature.vue';

export default {
  name: 'Dataset',
  components: {
    Feature,
  },
  data() {
    return {
      dataset: {},
      features: [],
      brokenFeaturesChecked: false,
    };
  },
  methods: {
    storeFeatures(features) {
      this.features = features;
    },
    onDatasetUploading() {

    },
    onDatasetUploaded(dataset) {
      this.processDataset(dataset);
    },
    processDataset(dataset) {
      this.dataset = dataset;
      const path = `http://localhost:3000/datasets/${dataset.dataset_id}/process`;

      axios.put(path)
        .then((res) => {
          this.storeFeatures(res.data.data.features_details);
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
  },
  computed: {
    skeletonDownloadLink() {
      return this.dataset ? `http://localhost:3000/datasets/${this.dataset.dataset_id}/download` : '#';
    },
    skeletonDownloadIcon() {
      return this.features.length > 0 ? 'cloud_download' : 'cloud_off';
    },
    skeletonDownloadDescription() {
      return this.features.length > 0 ? 'Download skeleton' : 'Skeleton not available';
    },
    featuresDescription() {
      return this.features.length > 0 ? `(${this.totalFeaturesCount}) Features` : 'No features yet...';
    },
    totalFeaturesCount() {
      return this.features.map((f) => f.total_count).reduce((a, b) => a + b, 0);
    },
    displayableFeatures() {
      if (this.brokenFeaturesChecked) {
        return this.features.filter((f) => f.has_broken_xlinks);
      }
      return this.features;
    },
  },
  mounted() {
    const self = this;
    EventBus.$on('dataset-uploading', () => self.onDatasetUploading());
    EventBus.$on('dataset-uploaded', (dataset) => self.onDatasetUploaded(dataset));
    EventBus.$on('dataset-selected', (dataset) => self.processDataset(dataset));
  },
};
</script>
