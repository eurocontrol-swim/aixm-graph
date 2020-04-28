// Copyright 2020 EUROCONTROL
// ==========================================

// Redistribution and use in source and binary forms, with or without modification, are permitted
// provided that the following conditions are met:

// 1. Redistributions of source code must retain the above copyright notice, this list of conditions
//    and the following disclaimer.
// 2. Redistributions in binary form must reproduce the above copyright notice, this list of
//    conditions and the following disclaimer in the documentation and/or other materials provided
//    with the distribution.
// 3. Neither the name of the copyright holder nor the names of its contributors may be used to
//    endorse or promote products derived from this software without specific prior written
//    permission.

// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
// IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
// FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
// CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
// DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
// DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
// WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
// ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

// ==========================================

// Editorial note: this license is an instance of the BSD license template as provided by the Open
// Source Initiative: http://opensource.org/licenses/BSD-3-Clause

// Details on EUROCONTROL: http://www.eurocontrol.int

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
                        <input type="checkbox" v-model="brokenFeatureTypesCheckbox">
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
      <feature-type v-for="featureType in displayableFeatureTypes"
               :featureType="featureType"
               :key="featureType.name"
               :datasetId="dataset.id">
      </feature-type>
    </ul>
  </div>

</template>

<script>
import EventBus from '../event-bus';
import FeatureType from './FeatureType.vue';
import FeatureTypeModel from '../models/FeatureType';
import DatasetModel from '../models/Dataset';
import * as serverApi from '../server-api';
import * as alert from '../alert';

export default {
  name: 'Dataset',
  components: {
    FeatureType,
  },
  data() {
    return {
      dataset: new DatasetModel(),
      brokenFeatureTypesCheckbox: false,
      loaderText: '',
    };
  },
  methods: {
    onDatasetUploading() {
      this.loaderText = 'Uploading...';
      this.dataset = new DatasetModel();
      this.brokenFeatureTypesCheckbox = false;
    },
    onDatasetUploaded(dataset) {
      this.dataset = dataset;
      this.loaderText = 'Processing...';
      this.getFeatureTypes();
    },
    onDatasetSelected(dataset) {
      this.dataset = dataset;
      if (dataset.featureTypes.length > 0) {
        return;
      }
      this.loaderText = 'Loading...';
      this.getFeatureTypes();
    },
    getFeatureTypes() {
      serverApi.getFeatureTypes(this.dataset.id)
        .then((res) => {
          this.loaderText = '';
          res.data.data.feature_types.forEach((featureType) => {
            this.dataset.featureTypes.push(
              new FeatureTypeModel(
                featureType.name,
                featureType.size,
                featureType.features_num_with_broken_xlinks,
              ),
            );
          });
        })
        .catch((error) => {
          this.loaderText = '';
          // eslint-disable-next-line
          console.error(error.response);
          alert.showError('Failed to process dataset!');
        });
    },
  },
  computed: {
    skeletonDownloadLink() {
      return this.dataset.id ? serverApi.getDownloadSkeletonURL(this.dataset.id) : '#';
    },
    skeletonDownloadIcon() {
      return this.dataset.featureTypes.length > 0 ? 'cloud_download' : 'cloud_off';
    },
    skeletonDownloadDescription() {
      return this.dataset.featureTypes.length > 0 ? 'Download skeleton' : 'Skeleton not available';
    },
    featuresDescription() {
      return this.dataset.featureTypes.length > 0 ? `(${this.totalFeaturesCount}) Features` : 'No features yet...';
    },
    totalFeaturesCount() {
      return this.dataset.featureTypes.map((ft) => ft.totalCount).reduce((a, b) => a + b, 0);
    },
    displayableFeatureTypes() {
      if (this.brokenFeatureTypesCheckbox) {
        return this.dataset.featureTypes.filter((ft) => ft.featuresNumWithBrokenXlinks > 0);
      }
      return this.dataset.featureTypes;
    },
  },
  mounted() {
    EventBus.$on('dataset-uploading', () => this.onDatasetUploading());
    EventBus.$on('dataset-uploaded', (dataset) => this.onDatasetUploaded(dataset));
    EventBus.$on('dataset-selected', (dataset) => this.onDatasetSelected(dataset));
  },
};
</script>

<style scoped>

.sidenav li > a {
  font-size: 12px;
}

.sidenav li > a > i, .sidenav li > a > i.material-icons {
  margin: 0 10px 0 0;
}

.sidenav {
  top: 64px;
  height: 100%;
  width: 380px;
}

.sidenav .divider {
  margin: 0px;
}
</style>
