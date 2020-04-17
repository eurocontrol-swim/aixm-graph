<template>
  <div id="graph-area">
    <div class="row valign-wrapper" :class="{hide: featureGroupName === null}">

      <div class="col s6">
        <p v-html="summary"></p>
      </div>

      <div class="col s2">
        <div class="input-field" :class="{hide: filterHidden}">
          <input type="text"
                 v-model="query"
                 @keypress.enter="onFilterFeatures">
          <label>Filter by field value</label>
        </div>
      </div>

      <div class="col s2">
        <div id="input-field" class="input-field" :class="{hide: filterHidden}">
          <select v-model="featuresPerPage"
                  ref="featuresPerPage">
            <option v-for="option in featuresPerPageOptions"
                    :value="option.value"
                    :key="option.value">
                    {{ option.text }}
            </option>
          </select>
          <label>Features per page</label>
        </div>
      </div>

      <div class="col s1">
        <p class="right">{{ paginationSummary }}</p>
      </div>

      <div class="col s1">
        <div :class="{hide: singleFeature !== null}">
          <a class="waves-effect waves-light btn btn-small red lighten-2"
             @click="getPrevPage" :disabled="prevOffset === null">
            <i class="material-icons">chevron_left</i>
          </a>
          <a class="waves-effect waves-light btn btn-small red lighten-2 right"
             @click="getNextPage" :disabled="nextOffset === null">
            <i class="material-icons">chevron_right</i>
          </a>
        </div>
      </div>
    </div>

        <!--          Graph area-->
    <div class="row graph-area" :class="{hide: featureGroupName === null}">
      <div class="progress" id="graphLoader" :class="{hide: loadingGraph === false}">
        <div class="indeterminate"></div>
      </div>
      <div class="col s12 valign-wrapper" id="graph" ref="graph"></div>
      <div class="collection" id="associations-select" :class="{hide: featureGroupName === null}">
        <a href="#!" class="collection-item active" @click="onClickAllAssociations">
          <i class="material-icons left">{{ allAssociationsIcon }}</i>
          Associations
        </a>

        <a href="#!" class="collection-item" v-for="association in associations"
          :association="association"
          :key="association.name"
          @click="onClickAssociation(association.name)">
          ({{ association.nodes.length }}) {{ association.name }}
          <i class="material-icons left" ref="checkboxIcon">
            {{ getAssociationIcon(association) }}
          </i>
        </a>
      </div>
    </div>

    <textarea readonly id="copyPasteArea" ref="copyPasteArea" v-model="currentHoveredFeatureNodeId">
    </textarea>

    <GlobalEvents
      @keydown.ctrl.67="copyNodeIdToClipboard"
    />
  </div>
</template>

<script>
import GlobalEvents from 'vue-global-events';
import Vue from 'vue';
import EventBus from '../event-bus';
import GraphModel from './GraphModel';
import * as serverApi from '../server-api';
import * as alert from '../alert';

/*
NOTE: We keep the graphModel out of the component scope because of differences in vue.js and vis.js
      implementations. More details here: https://github.com/almende/vis/issues/2567
*/
let graphModel = null;


// register globally
Vue.component('GlobalEvents', GlobalEvents);

export default {
  name: 'Graph',
  components: { GlobalEvents },
  data() {
    return {
      datasetId: null,
      featureGroupName: null,
      singleFeature: null,
      query: '',
      featuresPerPage: 5,
      featuresPerPageOptions: [5, 10, 15, 20].map((i) => ({ text: i, value: i })),
      allAssociationsSelected: true,
      associations: [],
      nextOffset: null,
      prevOffset: null,
      summary: '',
      paginationSummary: '',
      loadingGraph: false,
      currentHoveredFeatureNodeId: null,
    };
  },
  methods: {
    reset(datasetId) {
      graphModel = null;
      this.datasetId = datasetId;
      this.featureGroupName = null;
      this.singleFeature = null;
      this.query = '';
      this.featuresPerPage = 5;
      this.allAssociationsSelected = true;
      this.associations = [];
      this.nextOffset = null;
      this.prevOffset = null;
      this.summary = '';
      this.paginationSummary = '';
      this.loadingGraph = false;
      this.currentHoveredFeatureNodeId = null;
    },
    onFilterFeatures() {
      this.getFeatureGroupGraph({ offset: 0 });
    },
    createGraphModel(data) {
      graphModel = new GraphModel(this.$refs.graph, data);
      graphModel.on('click', this.onClickGraphFeature);
      graphModel.on('oncontext', this.onRightClickGraphFeature);
      graphModel.on('hoverNode', this.onHoverFeatureNode);
    },
    initGraph(data) {
      this.createGraphModel(data);
      this.registerAssociations();
    },
    getFeatureGroupGraph({ offset }) {
      this.loadingGraph = true;
      serverApi.getFeatureGroupGraph({
        datasetId: this.datasetId,
        featureGroupName: this.featureGroupName,
        offset,
        limit: this.featuresPerPage,
        filterQuery: this.query,
      })
        .then((res) => {
          this.initGraph(res.data.data.graph);
          this.updatePagination(res.data.data);
          this.updateSummary();
          this.loadingGraph = false;
        })
        .catch((error) => {
          this.loadingGraph = false;
          // eslint-disable-next-line
          console.error(error.response);
          alert.showError('Failed to get features!');
        });
    },
    registerAssociations() {
      const associations = {};

      graphModel.getNodes().forEach((node) => {
        if (node.name !== this.featureGroupName) {
          if (associations[node.name] === undefined) {
            associations[node.name] = {
              nodes: [], selected: true, name: node.name,
            };
          }
          associations[node.name].nodes.push(node);
        }
      });
      this.associations = Object.values(associations);
    },
    onClickGraphFeature(params) {
      const featureId = params.nodes[0];

      if (featureId === undefined) {
        return;
      }

      this.loadingGraph = true;
      serverApi.getFeatureGraph(this.datasetId, featureId)
        .then((res) => {
          graphModel.update(res.data.data.graph);
          this.loadingGraph = false;
        })
        .catch((error) => {
          this.loadingGraph = false;
          // eslint-disable-next-line
          console.error(error);
          alert.showError('Failed to expand graph!');
        });
    },
    onRightClickGraphFeature(params) {
      params.event.preventDefault();

      const featureId = graphModel.getNodeIdAtPointer(params.pointer.DOM);

      if (featureId === undefined) {
        return;
      }

      const featureName = graphModel.getNodeById(featureId).name;

      this.singleFeature = featureName;
      this.summary = `<strong>${featureName}</strong> with id: <strong>${featureId}</strong>`;
      this.paginationSummary = '';

      this.loadingGraph = true;
      serverApi.getFeatureGraph(this.datasetId, featureId)
        .then((res) => {
          this.createGraphModel(res.data.data.graph);
          this.loadingGraph = false;
        })
        .catch((error) => {
          this.loadingGraph = false;
          // eslint-disable-next-line
          console.error(error.response);
          alert.showError('Failed to fetch feature graph!');
        });
    },
    onHoverFeatureNode(params) {
      this.currentHoveredFeatureNodeId = params.node;
    },
    onFeatureGroupSelected(datasetId, featureGroupName) {
      if (featureGroupName === this.featureGroupName) {
        return;
      }

      this.datasetId = datasetId;
      this.featureGroupName = featureGroupName;

      this.singleFeature = null;
      this.allAssociationsSelected = true;

      this.getFeatureGroupGraph({ offset: 0 });
    },
    onClickAllAssociations() {
      this.allAssociationsSelected = !this.allAssociationsSelected;

      const self = this;
      this.associations.forEach((assoc) => {
        if (assoc.selected !== this.allAssociationsSelected) {
          self.onClickAssociation(assoc.name);
        }
      });
    },
    onClickAssociation(associationName) {
      const association = this.associations.filter((assoc) => assoc.name === associationName)[0];
      association.selected = !association.selected;

      // update the 'all' checkbox
      if (!association.selected) {
        this.allAssociationsSelected = false;
      }

      if (this.associations.every((a) => a.selected)) {
        this.allAssociationsSelected = true;
      }

      this.updateGraphAssociations(association);
    },
    updateGraphAssociations(association) {
      if (association.selected) {
        association.nodes.forEach((node) => {
          graphModel.addNode(node);
        });
      } else {
        const associationsNodeIds = this.associations.reduce(
          (nodeIds, assoc) => nodeIds.concat(assoc.nodes.map((node) => node.id)), [],
        );

        const featureGroupNodeIds = graphModel.getNodes().getIds().filter(
          (id) => graphModel.getNodeById(id).name === this.featureGroupName,
        );

        const excludedNodeIds = featureGroupNodeIds.concat(associationsNodeIds);

        association.nodes.forEach((node) => {
          try {
            const branchIdsToRemove = graphModel.getBranchIds(node.id, [], excludedNodeIds);
            branchIdsToRemove.forEach((nodeId) => {
              graphModel.removeNodeById(nodeId);
            });
          } catch (error) {
          // eslint-disable-next-line
            console.error(error);
            alert.showError('Failed to update associations!');
          }
          graphModel.removeNodeById(node.id);
        });
      }
    },
    getPrevPage() {
      this.getFeatureGroupGraph({ offset: this.prevOffset });
    },
    getNextPage() {
      this.getFeatureGroupGraph({ offset: this.nextOffset });
    },
    getAssociationIcon(association) {
      return association.selected ? 'check_box' : 'check_box_outline_blank';
    },
    updateSummary() {
      this.summary = `<strong>${this.featureGroupName}</strong> features`;

      if (this.query) {
        this.summary += ` matching filter query '<strong>${this.query}</strong>'`;
      }
    },
    updatePagination(response) {
      this.nextOffset = response.next_offset;
      this.prevOffset = response.prev_offset;
      this.updatePaginationSummary(response.offset, response.limit, response.size);
    },
    updatePaginationSummary(offset, limit, size) {
      const upperLimit = (size - offset) < limit ? size : offset + limit;

      this.paginationSummary = `${offset + 1}-${upperLimit} of ${size}`;
    },
    copyNodeIdToClipboard() {
      this.$refs.copyPasteArea.select();
      document.execCommand('copy');
    },
  },
  computed: {
    allAssociationsIcon() {
      return this.allAssociationsSelected ? 'check_box' : 'check_box_outline_blank';
    },
    filterHidden() {
      return this.featureGroupName === null || this.singleFeature !== null;
    },
  },
  watch: {
    featuresPerPage() {
      this.getFeatureGroupGraph({ offset: 0 });
    },
  },
  created() {
    EventBus.$on('feature-group-selected', (datasetId, featureGroupName) => {
      this.onFeatureGroupSelected(datasetId, featureGroupName);
    });
    EventBus.$on('dataset-uploading', () => this.reset());
    EventBus.$on('dataset-uploaded', (dataset) => {
      this.datasetId = dataset.id;
    });
    EventBus.$on('dataset-selected', (dataset) => this.reset(dataset.id));
  },
};
</script>

<style>

.graph-area {
    height: 100%;
}

#graph-area {
  padding-left: 380px;
  height: 86%;
}


#graph {
   border: 1px solid lightgray;
   height: 100%;
   width: 100%;
}

#associations-select {
    position: absolute;
    left: 400px;
}

#associations-select li{
    padding-left: 20px;
}

#graphLoader {
  position: absolute;
}

#copyPasteArea {
  position: 'absolute';
  left: '-9999px';
  z-index: -1;
}

</style>
