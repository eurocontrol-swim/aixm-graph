

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
  template:
  `
     <li>
        <a class="waves-effect collection-item active" href="#!">
             ({{ feature.total_count }}) {{ feature.name}}
          <i v-if="feature.has_broken_xlinks" class="material-icons" id="report-icon">report</i>
          <i v-else="feature.has_broken_xlinks" class="material-icons" id="ok-icon">done</i>
          </a>
     </li>
  `
});


var sidenav = new Vue({
    el: '#side-nav',
    data: {
        filename: null,
        features: [],
    },
    methods: {
        init: function() {
            $('.collapsible').collapsible();
            $('.sidenav').sidenav();
            $('.modal').modal();
            $('.tooltipped').tooltip();
        },
        uploadAndValidate: function() {
            var self = this;
            var formData = new FormData(),
                fileInputElement = $("#aixm-upload")[0];

            formData.append("file", this.$refs.fileInput.files[0]);

            $.ajax({
                url: '/upload',
                type: 'POST',
                data: formData,
                contentType: false,
                processData: false,
                success: function(response){
                    self.hideProgress();
                    self.filename = response.filename;
                    self.validate()
                },
            });
            this.filename = "";
            this.$refs.featuresTitle.innerHTML = "No features yet";
            this.features = []
            this.showProgress('Uploading...');
            this.disableSkeleton()
            main.hide();
        },
        validate: function() {
            var self = this;
            $.ajax({
                type: "POST",
                url: "/validate",
                dataType : "json",
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify({filename: self.filename}),
                success : function(response) {
                    self.hideProgress();
                    self.$refs.featuresTitle.innerHTML = "Features (" + response.total_count + ")";
                    self.enableSkeleton()
                    response.features_details.forEach(function(data) {
                        self.features.push(data);
                    });
                }
            });

            this.showProgress('Validating features...');
        },
        download: function() {
            $.ajax({
                url: '/download-aixm',
                type: 'GET',
                contentType: false,
                processData: false,
                success: function(response){
                    console.table(response);
                },
            });
        },
        selectFeature: function(feature) {
            main.createGraphForFeature(feature);
        },
        showProgress: function(text) {
            this.$refs.progress.innerHTML = '<a class="center-align" id="progress-text">' + text + '</a>';
            this.$refs.progress.setAttribute('class', '');
            this.$refs.progressBar.setAttribute('class', '');

        },
        hideProgress: function() {
            this.$refs.progress.setAttribute('class', 'hide');
            this.$refs.progressBar.setAttribute('class', 'hide');
        },
        enableSkeleton: function() {
            this.$refs.skeleton.innerHTML = `
              <i class="material-icons" ref="skeleton">cloud_downloadff</i>
              Download skeleton`;

        },
        disableSkeleton: function() {
            this.$refs.skeleton.innerHTML = `
              <i class="material-icons" ref="skeleton">cloud_off</i>
              Skeleton not available`;
        }
    }
});


var main = new Vue({
    el: 'main',
    data: {
        filterKey: null,
        selectedFeature: null
    },
    methods: {
        show: function() {
            this.$el.setAttribute('class', '');
        },
        hide: function() {
            this.$el.setAttribute('class', 'hide');
        },
        createGraphForFeature: function(feature) {
            this.selectedFeature = feature;
            var that = this;
            this.show();
            $.ajax({
                type: "GET",
                url: "/graph/" + feature.name,
                dataType : "json",
                contentType: "application/json; charset=utf-8",
                success : function(result) {
                    createGraph(result.graph)
                    that.focusFilter(feature.name);
                    that.updateDescription(result.offset, result.limit, result.total_count)
                }
            });

        },
        filter: function() {
            var that = this;
            $.ajax({
                type: "GET",
                url: "/graph/" + this.selectedFeature.name + "?key=" + this.filterKey,
                dataType : "json",
                contentType: "application/json; charset=utf-8",
                success : function(result) {
                    createGraph(result.graph)
                    that.updateDescription(result.offset, result.limit, result.total_count)
                }
            });
        },
        focusFilter: function(featureName) {
            this.$refs.filter.focus();
            this.$refs.filter.setAttribute('placeholder', 'Filter ' + featureName + ' by key');
            this.$refs.description.innerHTML = "Displaying all " + featureName + " features";
        },
        updateDescription: function(offset, limit, totalCount) {
            if (offset == null) {
                paging = " <strong>" + totalCount + "</strong> of <strong>" + totalCount + "</strong> "
            }
            else {
                paging =  " <strong>" + offset + "-" + limit + "</strong> of <strong>" + totalCount + "</strong> "
            }

            var html = "Displaying " + paging + this.selectedFeature.name + " features";

            if (this.filterKey != null) {
                html += " with matching key <strong>" + this.filterKey + "</strong>"
            }
            this.$refs.description.innerHTML = html;
        }
    }
});
