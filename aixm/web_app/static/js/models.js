

var featuresList = new Vue({
    el: '#features-list',
    data: {
        features: [],
        selectedFeature: null
    },
    methods: {
        add: function(feature_data){
            this.features.push(feature_data)
        },
        setSelectedFeature(feature) {
            this.selectedFeature = feature;

            filterFeatures.activate();
            filterFeatures.focus();
        }
    }
})


var filterFeatures = new Vue({
    el: '#filterFeatures',
    data: {
        key: null,
        active: false
    },
    methods: {
        filter: function() {
            $.ajax({
                type: "GET",
                url: "/graph/" + featuresList.selectedFeature.name + "?key=" + this.key,
                dataType : "json",
                contentType: "application/json; charset=utf-8",
                success : function(result) {
                    createGraph(result.graph)
                }
            });
        },
        focus: function() {
            this.$refs.filter.focus();
        },
        activate: function() {
            if (!this.active) {
                this.active = true;
            }
        }
    },
    computed: {
        selectedFeature: function() {
            return featuresList.selectedFeature.name;
        }
    }
});


Vue.component('feature-item', {
  props: ['feature'],
  template: `
      <a class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" v-on:click="updateGraph(feature)" role="tab" data-toggle="list" href="">
          {{ feature.name }}
          <span v-if="feature.has_broken_xlinks" class="badge badge-warning">{{ feature.count }} <i class="fas fa-exclamation-triangle"></i></span>
          <span v-else="feature.has_broken_xlinks" class="badge badge-success">{{ feature.count }}</span>

      </a>
  `,
  methods: {
    updateGraph: function(feature) {
        $.ajax({
            type: "GET",
            url: "/graph/" + feature.name,
            dataType : "json",
            contentType: "application/json; charset=utf-8",
            success : function(result) {
                createGraph(result.graph)
            }
        });
    }
  }
});

