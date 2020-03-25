
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


var Sidenav = new Vue({
    el: '#side-nav',
    data: {
        filename: null,
        fileId: null,
        features: [],
        displayFeatures: [],
        selectedFeature: null
    },
    methods: {
        init: function() {
            $('.collapsible').collapsible();
            $('.sidenav').sidenav();
            $('.modal').modal();
            $('.tooltipped').tooltip();
        },
        addFeature: function(data) {
            this.features.push(data);
        },
        resetFeatures: function() {
            this.features = [];
            this.displayFeatures = [];
        },
        prepareLoad: function() {
            this.filename = "";
            this.$refs.featuresTitle.innerHTML = 'No features yet <i class="material-icons">arrow_drop_down</i>';
            this.resetFeatures();
            this.disableSkeleton();
        },
        fileLoaded: function(filename, fileId) {
            this.hideProgress();
            this.filename = filename;
            this.fileId = fileId;
            this.process(fileId);
        },
        process: function(fileId) {
            var self = this;
            $.ajax({
                type: "PUT",
                url: "/files/" + fileId + "/process",
                dataType : "json",
                contentType: "application/json; charset=utf-8",
                data: {},
                success: function(response) {
                    self.hideProgress();
                    self.$refs.featuresTitle.innerHTML = 'Features (' + response.data.total_count + ') <i class="material-icons">arrow_drop_down</i>';
                    self.enableSkeleton()
                    response.data.features_details.forEach(function(data) {
                        self.addFeature(data);
                    });
                    self.setDisplayableFeatures();
                },
                error: function(response) {
                    showError('File process failed!')
                    console.log(response.responseJSON.error);
                    self.hideProgress();
                }
            });

            this.showProgress('Processing file...');
        },
        getGraphForFeature: function(feature) {
            var that = this;
            $.ajax({
                type: "GET",
                url: "/files/" + this.fileId + "/features/graph?name=" + feature.name + "&offset=0"  + "&limit=" + Main.featuresPerPage,
                dataType : "json",
                contentType: "application/json; charset=utf-8",
                success : function(response) {
                    that.selectedFeature = feature;
                    Main.drawGraph(response.data.graph, response.data.offset, response.data.limit, response.data.total_count);
                },
                error: function() {
                    console.log(response.responseJSON.error);
                    showError('Failed to get the graph for ' + feature.name);
                }
            });
            Main.showGraphLoader();
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
            var downloadLink = "/files/" + this.fileId + "/download";
            this.$refs.skeleton.innerHTML = `
              <i class="material-icons" ref="skeleton">cloud_downloadff</i>
              Download skeleton`;
            this.$refs.skeleton.setAttribute('href', downloadLink)
        },
        disableSkeleton: function() {
            this.$refs.skeleton.innerHTML = `
              <i class="material-icons" ref="skeleton">cloud_off</i>
              Skeleton not available`;
            this.$refs.skeleton.setAttribute('href', "")
        },
        setDisplayableFeatures: function() {
            if (this.$refs.featuresCheckbox.checked) {
                this.displayFeatures = this.features.filter((f) => f.has_broken_xlinks);
            }
            else {
                this.displayFeatures = this.features;
            }
         }
    }
});


var Main = new Vue({
    el: 'main',
    data: {
        filterKey: null,
        featuresPerPage: 5,
        featuresPerPageOptions: [
            { text: '5', value: 5 },
            { text: '10', value: 10 },
            { text: '15', value: 15 },
            { text: '20', value: 20 },
        ],
        nextOffset: null,
        prevOffset: null,
        filterNullified: true
    },
    methods: {
        show: function() {
            this.$el.setAttribute('class', '');
        },
        hide: function() {
            this.$el.setAttribute('class', 'hide');
        },
        showGraphLoader: function() {
            this.$refs.graph.innerHTML = `
                  <div class="preloader-wrapper big active graph-loader" ref="graphLoader">
                    <div class="spinner-layer spinner-blue-only">
                      <div class="circle-clipper left">
                        <div class="circle"></div>
                      </div><div class="gap-patch">
                        <div class="circle"></div>
                      </div><div class="circle-clipper right">
                        <div class="circle"></div>
                      </div>
                    </div>
                  </div>
            `
//            this.$refs.graphLoader.setAttribute('class', '');
        },
        drawGraph: function(graph, offset, limit, total_count) {
            this.show();
            createGraph(graph)
            this.focusFilter(Sidenav.selectedFeature.name);
            this.updateDescription()
            this.updatePagination(offset, limit, total_count)
        },
        filter: function(event) {
            if (event.key == 'Backspace' || (event.keyCode >= 65 && event.keyCode <= 90) || (event.keyCode >= 48 && event.keyCode <= 57)) {
                if (event.key == 'Backspace' && this.filterNullified) {
                    this.updateDescription()
                    return;
                }
                this.getGraph(0);
                this.filterNullified = !this.filterKey;
            }
        },
        getGraph: function(offset) {
            offset = (!offset) ? 0 : offset;
            var keyQuery = (!this.filterKey)?"":"key=" + this.filterKey;

            var that = this;
            $.ajax({
                type: "GET",
                url: "/files/" + Sidenav.fileId + "/features/graph?name=" + Sidenav.selectedFeature.name + "&" + keyQuery + "&offset=" + offset + "&limit=" + this.featuresPerPage,
                dataType : "json",
                contentType: "application/json; charset=utf-8",
                success : function(response) {
                    createGraph(response.data.graph)
                    that.updateDescription()
                    that.updatePagination(response.data.offset, response.data.limit, response.data.total_count)
                },
                error: function(response) {
                    console.log(response.responseJSON.error);
                    showError('Failed to get the graph for ' + Sidenav.selectedFeature.name);
                }
            });
            this.showGraphLoader();
        },
        focusFilter: function(featureName) {
            this.$refs.filter.removeAttribute('disabled');
            this.$refs.filter.focus();
        },
        disableFilter: function() {
            this.filterKey = null;
            this.$refs.filter.setAttribute('disabled', '');
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
            var text = "<strong>" + Sidenav.selectedFeature.name + "</strong> features";

            if (this.filterKey) {
                text += " with matching key <strong>'" + this.filterKey + "'</strong>"
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
            this.getGraph(this.nextOffset)
        },
        prevPage: function() {
            this.getGraph(this.prevOffset)
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


Vue.component('file-item-dropdown', {
  props: ['file'],
  template:
  `
    <li>
        <a href="#">
            {{ file.filename }}
        </a>
    </li>
  `
});


var Nav = new Vue({
    el: '#nav',
    data: {
        files: []
    },
    methods: {
        uploadFile: function() {
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
                    self.files.push(response.data)
                    Sidenav.fileLoaded(response.data.filename, response.data.file_id);
                },
                error: function(response) {
                    self.hideProgress();
                    console.log(response.responseJSON.error);
                    showError('File upload failed')
                }
            });
            Sidenav.showProgress('Uploading...');
            Sidenav.prepareLoad();
            Main.hide();
        },
        loadFile: function(file) {
            Sidenav.prepareLoad();
            Main.hide();
            Sidenav.fileLoaded(file.filename, file.file_id);
        }
    }
});

