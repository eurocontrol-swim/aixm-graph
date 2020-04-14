<template>
  <div id="graph-area">
    <div class="row valign-wrapper">
      <div class="col s2">
        <div class="input-field">
          <input type="text" v-model="query" @keypress.enter="onFilterFeatures">
          <label>Filter by field value</label>
        </div>
      </div>

      <div class="col s2">
        <div id="input-field" class="input-field">
          <select v-model="featuresPerPage">
            <option v-for="option in featuresPerPageOptions"
                    :value="option.value"
                    :key="option.value">
                    {{ option.text }}
            </option>
          </select>
          <label>Features per page</label>
        </div>
      </div>

      <div class="col s6">
        <p class="right">{{ graphSummary }}</p>
      </div>

      <div class="col s1">
        <p class="right">{{ paginationSummary }}</p>
      </div>

      <div class="col s1">
        <div>
          <a class="waves-effect waves-light btn btn-small red lighten-2"
             @:click="getPrevPage" >
            <i class="material-icons">chevron_left</i>
          </a>
          <a class="waves-effect waves-light btn btn-small red lighten-2 right"
             @:click="getNextPage" >
            <i class="material-icons">chevron_right</i>
          </a>
        </div>
      </div>
    </div>

        <!--          Graph area-->
    <div class="row graph-area">
      <div class="col s12 valign-wrapper" id="graph" ref="graph"></div>
      <div class="collection" id="associations-select">
        <a href="#!" class="collection-item active" @click="onClickAllAssociations">
          <i class="material-icons left">{{ allAssociationsIcon }}</i>
          Associations
        </a>

        <a href="#!" class="collection-item" v-for="association in associations"
          :association="association"
          :key="association.name"
          @click="onClickAssociation(association.name)">
          ({{ association.nodesData.length }}) {{ association.name }}
          <i class="material-icons left" ref="checkboxIcon">
            {{ getAssociationIcon(association) }}
          </i>
        </a>
      </div>
    </div>
  </div>
</template>

<script>
import EventBus from '../event-bus';
import * as network from './network';
import * as serverApi from '../server-api';

export default {
  name: 'Graph',
  data() {
    return {
      network: null,
      datasetId: null,
      featureGroup: null,
      query: '',
      featuresPerPage: 5,
      featuresPerPageOptions: [5, 10, 15, 20].map((i) => ({ text: i, value: i })),
      allAssociationsSelected: false,
      associations: [{ name: 'alex', selected: false, nodesData: [] }],
    };
  },
  methods: {
    onFilterFeatures() {
      this.getFeatureGroupGraph({ offset: 0 });
    },
    getFeatureGroupGraph({ offset }) {
      serverApi.getFeatureGroupGraph({
        datasetId: this.datasetId,
        featureGroup: this.featureGroup,
        offset,
        limit: this.featuresPerPage,
        filterQuery: this.query,
      })
        .then((res) => {
          const data = res.data.data.graph;
          this.network = network.createNetwork(
            this.$refs.graph, data.nodes, data.edges,
          );
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    onFeatureGroupSelected(datasetId, featureGroup) {
      this.datasetId = datasetId;
      this.featureGroup = featureGroup;

      this.getFeatureGroupGraph({ offset: 0 });
    },
    onClickAllAssociations() {
      this.allAssociationsSelected = !this.allAssociationsSelected;
    },
    onClickAssociation(associationName) {
      const association = this.associations.filter((assoc) => assoc.name === associationName)[0];
      association.selected = !association.selected;
    },
    getPrevPage() {

    },
    getNextPage() {

    },
    getAssociationIcon(association) {
      return association.selected ? 'check_box' : 'check_box_outline_blank';
    },
  },
  computed: {
    graphSummary() {
      return 'alex';
    },
    paginationSummary() {
      return '5-10 of 100';
    },
    allAssociationsIcon() {
      return this.allAssociationsSelected ? 'check_box' : 'check_box_outline_blank';
    },
  },
  watch: {
    featuresPerPage() {
      this.getFeatureGroupGraph({ offset: 0 });
    },
  },
  created() {
    EventBus.$on('feature-group-selected', (datasetId, featureGroup) => {
      this.onFeatureGroupSelected(datasetId, featureGroup);
    });
  },
};
</script>

<style>

.graph-area {
    height: 100%;
}

#graph-area {
  padding-left: 380px;
  height: 87%;
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
</style>
