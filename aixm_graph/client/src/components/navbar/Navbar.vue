<template>
  <div>

    <!-- modal -->
    <div id="modal1" class="modal ">
      <div class="modal-content">
        <div class="row">
          <div class="col s12">
            <h5>Upload AIXM Dataset</h5>
          </div>
        </div>
        <div class="row">
          <div class="col s12">
            <form action="#">
              <div class="file-field input-field">
                <div class="btn">
                  <span>Dataset</span>
                  <input type="file" ref="fileInput" >
                </div>
                <div class="file-path-wrapper">
                  <input class="file-path process" type="text">
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <a class="modal-close waves-effect waves-green btn"
          v-on:click="uploadDataset()" type="submit">
          Upload & process
        </a>
      </div>
    </div>

    <!-- navbar -->
    <nav class="nav  blue lighten-1">
      <div class="nav-wrapper">
        <a href="#" class="brand-logo">AIXM Graph </a>
        <ul class="right hide-on-med-and-down">
          <li>
            <datasetslist :datasets="datasets"></datasetslist>
          </li>
          <li>

          <a class="btn red lighten-2 modal-trigger" href="#modal1" title="Upload AIXM dataset">
            <i class="material-icons left">cloud_upload</i>Upload
          </a>
          </li>
        </ul>
      </div>
    </nav>
  </div>
</template>


<script>
import axios from 'axios';
import DatasetsList from './DatasetsList.vue';

export default {
  name: 'Navbar',
  data() {
    return {
      datasets: [],
    };
  },
  components: {
    datasetslist: DatasetsList,
  },
  methods: {
    getDatasets() {
      const path = 'http://localhost:3000/load-datasets';
      axios.get(path)
        .then((res) => {
          // eslint-disable-next-line
          console.log(res);
          this.datasets = res.data.data;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    loadDataset() {

    },
    uploadDataset() {
      // const self = this;
      const formData = new FormData();

      formData.append('file', this.$refs.fileInput.files[0]);

      const path = 'http://localhost:3000/upload';
      axios.post(path, formData)
        .then((res) => {
          // store the dataset
          this.datasets.push(res.data.data);

          // eslint-disable-next-line
          console.log(res);

          // self.datasets.push(response.data)
          // Sidenav.datasetLoaded(response.data.dataset_name, response.data.dataset_id);
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);

          // self.hideProgress();
          // console.log(response.responseJSON.error);
          // showError('Dataset upload failed')
        });

      // Sidenav.showProgress('Uploading...');
      // Sidenav.prepareLoad();
      // Main.hide();
    },
  },

  created() {
    this.getDatasets();
  },
};
</script>

<style>

#dropdown-aixm-datasets {
    min-width: 400px;
}

</style>
