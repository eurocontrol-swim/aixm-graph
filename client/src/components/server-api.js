import axios from 'axios';

const config = {
  baseURL: 'http://localhost:3000/',
};

const getDatasets = () => axios.get('/datasets', config);

const uploadDataset = (formData) => axios.post('/upload', formData, config);

const processDataset = (datasetId) => axios.put(`/datasets/${datasetId}/process`, {}, config);

const getFeatureGroupGraph = ({
  datasetId,
  featureGroupName,
  offset = 0,
  limit,
  filterQuery = '',
}) => {
  const queryStr = `offset=${offset}&limit=${limit}&key=${filterQuery}`;

  return axios.get(
    `/datasets/${datasetId}/feature_groups/${featureGroupName}/graph?${queryStr}`,
    config,
  );
};

const getFeatureGraph = (datasetId, featureId) => axios.get(
  `/datasets/${datasetId}/features/${featureId}/graph`, config,
);

const getDownloadSkeletonURL = (datasetId) => `${config.baseURL}datasets/${datasetId}/download`;

export {
  getDatasets,
  uploadDataset,
  processDataset,
  getFeatureGroupGraph,
  getFeatureGraph,
  getDownloadSkeletonURL,
};
