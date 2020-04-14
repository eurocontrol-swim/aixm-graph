import axios from 'axios';

const baseUrl = 'http://localhost:3000';

const getDatasets = () => axios.get(`${baseUrl}/datasets`);

const uploadDataset = (formData) => axios.post(`${baseUrl}/upload`, formData);

const processDataset = (datasetId) => axios.put(`${baseUrl}/datasets/${datasetId}/process`);

const getFeatureGroupGraph = ({
  datasetId,
  featureGroup,
  offset = 0,
  limit,
  filterQuery = '',
}) => {
  const queryStr = `name=${featureGroup}&offset=${offset}&limit=${limit}&key=${filterQuery}`;

  return axios.get(`${baseUrl}/datasets/${datasetId}/features/graph?${queryStr}`);
};

const getDownloadSkeletonURL = (datasetId) => `${baseUrl}/datasets/${datasetId}/download`;

export {
  getDatasets,
  uploadDataset,
  processDataset,
  getFeatureGroupGraph,
  getDownloadSkeletonURL,
};
