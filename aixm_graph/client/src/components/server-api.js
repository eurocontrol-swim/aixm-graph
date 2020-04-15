import axios from 'axios';

const baseUrl = 'http://localhost:3000';

const getDatasets = () => axios.get(`${baseUrl}/datasets`);

const uploadDataset = (formData) => axios.post(`${baseUrl}/upload`, formData);

const processDataset = (datasetId) => axios.put(`${baseUrl}/datasets/${datasetId}/process`);

const getFeatureGroupGraph = ({
  datasetId,
  featureGroupName,
  offset = 0,
  limit,
  filterQuery = '',
}) => {
  const queryStr = `offset=${offset}&limit=${limit}&key=${filterQuery}`;

  return axios.get(`${baseUrl}/datasets/${datasetId}/feature_groups/${featureGroupName}/graph?${queryStr}`);
};

const getFeatureGraph = (datasetId, featureId) => axios.get(
  `${baseUrl}/datasets/${datasetId}/features/${featureId}/graph`,
);

const getDownloadSkeletonURL = (datasetId) => `${baseUrl}/datasets/${datasetId}/download`;

export {
  getDatasets,
  uploadDataset,
  processDataset,
  getFeatureGroupGraph,
  getFeatureGraph,
  getDownloadSkeletonURL,
};
