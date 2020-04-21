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

import axios from 'axios';

const isDev = Boolean(window.webpackHotUpdate);

const config = {
  baseURL: isDev ? 'http://localhost:5000' : '',
};

const getDatasets = () => axios.get('/api/datasets', config);

const uploadDataset = (formData) => axios.post('/api/upload', formData, config);

const processDataset = (datasetId) => axios.put(`/api/datasets/${datasetId}/process`, {}, config);

const getFeatureGroupGraph = ({
  datasetId,
  featureGroupName,
  offset = 0,
  limit,
  filterQuery = '',
}) => {
  const queryStr = `offset=${offset}&limit=${limit}&key=${filterQuery}`;

  return axios.get(
    `/api/datasets/${datasetId}/feature_groups/${featureGroupName}/graph?${queryStr}`, config,
  );
};

const getFeatureGraph = (datasetId, featureId) => axios.get(
  `/api/datasets/${datasetId}/features/${featureId}/graph`, config,
);

const getDownloadSkeletonURL = (datasetId) => `${config.baseURL}/api/datasets/${datasetId}/download`;

export {
  getDatasets,
  uploadDataset,
  processDataset,
  getFeatureGroupGraph,
  getFeatureGraph,
  getDownloadSkeletonURL,
};
