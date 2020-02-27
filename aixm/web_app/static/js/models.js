

var featuresList = new Vue({
    el: '#features-list',
    data: {
        features: []
    },
    methods: {
        add: function(feature_data){
            this.features.push(feature_data)
        }
    }
})


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
                console.log(result);
                reset_svg();
                update_graph(result.graph.links, result.graph.nodes);
            }
        });
    }
  }
});
