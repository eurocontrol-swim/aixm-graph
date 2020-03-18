
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
        selectedFeature: null,
        nextOffset: null,
        prevOffset: null
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
                url: "/graph/" + feature.name + "?offset=0",
                dataType : "json",
                contentType: "application/json; charset=utf-8",
                success : function(result) {
                    createGraph(result.graph)
                    that.focusFilter(feature.name);
                    that.updateDescription()
                    that.updatePagination(result.offset, result.limit, result.total_count)
                }
            });

        },
        filter: function(offset) {
            this.getGraph(this.filterKey, 0);
        },
        getGraph: function(key, offset) {
            offset = (!offset) ? 0 : offset;
            var keyQuery = (!key)?"":"key=" + key;

            var that = this;
            $.ajax({
                type: "GET",
                url: "/graph/" + this.selectedFeature.name + "?" + keyQuery + "&offset=" + offset,
                dataType : "json",
                contentType: "application/json; charset=utf-8",
                success : function(result) {
                    createGraph(result.graph)
                    that.updateDescription()
                    that.updatePagination(result.offset, result.limit, result.total_count)
                }
            });
        },
        focusFilter: function(featureName) {
            this.$refs.filter.removeAttribute('disabled');
            this.$refs.filter.focus();
            this.$refs.filter.setAttribute('placeholder', 'Filter ' + featureName + ' by key');
        },
        disableFilter: function() {
            this.$refs.filter.setAttribute('disabled', '');
            this.$refs.filter.setAttribute('placeholder', '');
        },
        updatePagination(offset, limit, total) {
            if (total <= limit) {
                text = total + " of " + total;
                this.disablePagination('prev')
                this.disablePagination('next')
            }
            else {
                from = offset + 1;
                to = ((offset + limit) <= total ) ? offset + limit : total;
                text = from + "-" + to + " of " + total;

                if (from > 1) {
                    this.prevOffset = offset - limit;
                    this.enablePagination('prev')
                }
                else {
                    this.disablePagination('prev')
                }

                if (to < total) {
                    this.nextOffset = offset + limit;
                    this.enablePagination('next')
                }
                else {
                    this.disablePagination('next')
                }
            }
            this.setPaginationText(text);
        },
        updateDescription: function() {
            var text = this.selectedFeature.name + " features";

            if (this.filterKey != null) {
                text += " with matching key <strong>" + this.filterKey + "</strong>"
            }
            this.setDescription(text);
        },
        setPaginationText: function(text) {
            this.$refs.pagination.innerHTML = text;
        },
        setDescription: function(text) {
            this.$refs.description.innerHTML = text;
        },
        nextPage: function() {
            this.getGraph(this.filterKey, this.nextOffset)
        },
        prevPage: function() {
            this.getGraph(this.filterKey, this.prevOffset)
        },
        enablePagination: function(direction) {
            paginationButton = (direction == "next") ? this.$refs.paginationNext : this.$refs.paginationPrev
            paginationButton.removeAttribute('disabled');
        },
        disablePagination: function(direction) {
            paginationButton = (direction == "next") ? this.$refs.paginationNext : this.$refs.paginationPrev
            paginationButton.setAttribute('disabled', '');
        }
    }
});
