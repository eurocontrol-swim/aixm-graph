import axios from 'axios';

const baseUrl = 'http://localhost:3000';

const getDatasets = () => axios.get(`${baseUrl}/datasets`);

const uploadDataset = (formData) => axios.post(`${baseUrl}/upload`, formData);

const processDataset = (datasetId) => axios.put(`${baseUrl}/datasets/${datasetId}/process`);

const getDownloadSkeletonURL = (datasetId) => `${baseUrl}/datasets/${datasetId}/download`;

export {
  getDatasets,
  uploadDataset,
  processDataset,
  getDownloadSkeletonURL,
};
