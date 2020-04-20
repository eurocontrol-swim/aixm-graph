import axios from 'axios';

const getDatasets = () => axios.get('/api/datasets');

const uploadDataset = (formData) => axios.post('/api/upload', formData);

const processDataset = (datasetId) => axios.put(`/api/datasets/${datasetId}/process`, {});

const getFeatureGroupGraph = ({
  datasetId,
  featureGroupName,
  offset = 0,
  limit,
  filterQuery = '',
}) => {
  const queryStr = `offset=${offset}&limit=${limit}&key=${filterQuery}`;

  return axios.get(
    `/api/datasets/${datasetId}/feature_groups/${featureGroupName}/graph?${queryStr}`,
  );
};

const getFeatureGraph = (datasetId, featureId) => axios.get(
  `/api/datasets/${datasetId}/features/${featureId}/graph`,
);

const getDownloadSkeletonURL = (datasetId) => `/api/datasets/${datasetId}/download`;

export {
  getDatasets,
  uploadDataset,
  processDataset,
  getFeatureGroupGraph,
  getFeatureGraph,
  getDownloadSkeletonURL,
};
