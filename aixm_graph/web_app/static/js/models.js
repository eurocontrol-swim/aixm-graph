
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
        selectedFeature: null
    },
    methods: {
        init: function() {
            $('.collapsible').collapsible();
            $('.sidenav').sidenav();
            $('.modal').modal();
            $('.tooltipped').tooltip();
        },
        prepareLoad: function() {
            this.filename = "";
            this.$refs.featuresTitle.innerHTML = "No features yet";
            this.features = [];
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
                    self.$refs.featuresTitle.innerHTML = "Features (" + response.data.total_count + ")";
                    self.enableSkeleton()
                    response.data.features_details.forEach(function(data) {
                        self.features.push(data);
                    });
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
                url: "/files/" + this.fileId + "/features/graph?name=" + feature.name + "&offset=0",
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
        }
    }
});


var Main = new Vue({
    el: 'main',
    data: {
        filterKey: null,
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
                    return;
                }
                this.getGraph(this.filterKey, 0);
                this.filterNullified = !this.filterKey;
            }
        },
        getGraph: function(key, offset) {
            offset = (!offset) ? 0 : offset;
            var keyQuery = (!key)?"":"key=" + key;

            var that = this;
            $.ajax({
                type: "GET",
                url: "/files/" + Sidenav.fileId + "/features/graph?name=" + Sidenav.selectedFeature.name + "&" + keyQuery + "&offset=" + offset,
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
        },
        focusFilter: function(featureName) {
            this.$refs.filter.removeAttribute('disabled');
            this.$refs.filter.focus();
            this.$refs.filter.setAttribute('placeholder', 'Filter ' + featureName + ' by key');
        },
        disableFilter: function() {
            this.filterKey = null;
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
            var text = "<strong>" + Sidenav.selectedFeature.name + "</strong> features";

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

