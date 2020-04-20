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
