<template>
  <div>

    <!-- modal -->
    <div id="modal1" class="modal ">
      <div class="modal-content">
        <div class="row">
          <div class="col s12">
            <h5>Upload Dataset</h5>
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
            <datasets-list :datasets="datasets"></datasets-list>
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
import DatasetsList from './DatasetsList.vue';
import EventBus from '../event-bus';
import DatasetModel from '../models/Dataset';
import * as serverApi from '../server-api';
import * as alert from '../alert';

export default {
  name: 'Navbar',
  data() {
    return {
      datasets: [],
    };
  },
  components: {
    DatasetsList,
  },
  methods: {
    getDatasets() {
      serverApi.getDatasets()
        .then((res) => {
          res.data.data.forEach((data) => {
            this.datasets.push(new DatasetModel(data.dataset_id, data.dataset_name));
          });
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error.response);
          alert.showError('Failed to retrieve datasets!');
        });
    },
    uploadDataset() {
      // const self = this;
      const formData = new FormData();

      formData.append('file', this.$refs.fileInput.files[0]);

      EventBus.$emit('dataset-uploading');

      serverApi.uploadDataset(formData)
        .then((res) => {
          const dataset = new DatasetModel(res.data.data.dataset_id, res.data.data.dataset_name);
          this.datasets.push(dataset);

          EventBus.$emit('dataset-uploaded', dataset);
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error.response);
          alert.showError('Failed to upload dataset!');
        });
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
