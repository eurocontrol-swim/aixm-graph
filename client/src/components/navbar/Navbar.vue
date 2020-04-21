// Copyright 2020 EUROCONTROL
// ==========================================

// Redistribution and use in source and binary forms, with or without modification, are permitted
// provided that the following conditions are met:

// 1. Redistributions of source code must retain the above copyright notice, this list of conditions
//    and the following disclaimer.
// 2. Redistributions in binary form must reproduce the above copyright notice, this list of
//    conditions and the following disclaimer in the documentation and/or other materials provided
//    with the distribution.
// 3. Neither the name of the copyright holder nor the names of its contributors may be used to
//    endorse or promote products derived from this software without specific prior written
//    permission.

// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
// IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
// FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
// CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
// DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
// DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
// WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
// ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

// ==========================================

// Editorial note: this license is an instance of the BSD license template as provided by the Open
// Source Initiative: http://opensource.org/licenses/BSD-3-Clause

// Details on EUROCONTROL: http://www.eurocontrol.int

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
