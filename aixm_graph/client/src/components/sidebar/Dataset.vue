<template>

  <div class="row" id="side-nav">

    <ul id="slide-out" class="sidenav sidenav-fixed" ref="sidenavList">
      <li :class="{'hide': loaderText === ''}">
        <a class="center-align" >{{ loaderText }}</a>
      </li>
      <li ref="progressBar" :class="{'hide': loaderText === ''}">
        <div class="progress"><div class="indeterminate"></div></div>
      </li>
      <li class="no-padding">
        <ul class="collapsible collapsible-accordion">
          <li>
            <a class="collapsible-header">
              Dataset: {{ dataset.name }}<i class="material-icons">arrow_drop_down</i>
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
                        <input type="checkbox" v-model="brokenFeatureGroupsCheckbox">
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
      <feature-group v-for="featureGroup in displayableFeatureGroups"
               :featureGroup="featureGroup"
               :key="featureGroup.name">
      </feature-group>
    </ul>
  </div>

</template>

<script>
import EventBus from '../event-bus';
import FeatureGroup from './FeatureGroup.vue';
import FeatureGroupModel from '../models/FeatureGroup';
import DatasetModel from '../models/Dataset';
import * as serverApi from '../server-api';

export default {
  name: 'Dataset',
  components: {
    FeatureGroup,
  },
  data() {
    return {
      dataset: new DatasetModel(),
      brokenFeatureGroupsCheckbox: false,
      loaderText: '',
    };
  },
  methods: {
    onDatasetUploading() {
      this.loaderText = 'Uploading...';
      this.dataset = new DatasetModel();
      this.brokenFeatureGroupsCheckbox = false;
    },
    onDatasetUploaded(dataset) {
      this.dataset = dataset;
      this.loaderText = 'Processing...';
      this.processDataset();
    },
    onDatasetSelected(dataset) {
      this.dataset = dataset;
      if (dataset.featureGroups.length > 0) {
        return;
      }
      this.loaderText = 'Loading...';
      this.processDataset();
    },
    processDataset() {
      serverApi.processDataset(this.dataset.id)
        .then((res) => {
          this.loaderText = '';
          res.data.data.feature_groups.forEach((fg) => {
            this.dataset.featureGroups.push(
              new FeatureGroupModel(fg.name, fg.total_count, fg.has_broken_xlinks),
            );
          });
        })
        .catch((error) => {
          this.loaderText = '';
          // eslint-disable-next-line
          console.error(error);
        });
    },
  },
  computed: {
    skeletonDownloadLink() {
      return this.dataset.id ? serverApi.getDownloadSkeletonURL(this.dataset.id) : '#';
    },
    skeletonDownloadIcon() {
      return this.dataset.featureGroups.length > 0 ? 'cloud_download' : 'cloud_off';
    },
    skeletonDownloadDescription() {
      return this.dataset.featureGroups.length > 0 ? 'Download skeleton' : 'Skeleton not available';
    },
    featuresDescription() {
      return this.dataset.featureGroups.length > 0 ? `(${this.totalFeaturesCount}) Features` : 'No features yet...';
    },
    totalFeaturesCount() {
      return this.dataset.featureGroups.map((fg) => fg.totalCount).reduce((a, b) => a + b, 0);
    },
    displayableFeatureGroups() {
      if (this.brokenFeatureGroupsCheckbox) {
        return this.dataset.featureGroups.filter((fg) => fg.hasBrokenXlinks);
      }
      return this.dataset.featureGroups;
    },
  },
  mounted() {
    const self = this;
    EventBus.$on('dataset-uploading', () => self.onDatasetUploading());
    EventBus.$on('dataset-uploaded', (dataset) => self.onDatasetUploaded(dataset));
    EventBus.$on('dataset-selected', (dataset) => self.onDatasetSelected(dataset));
  },
};
</script>
