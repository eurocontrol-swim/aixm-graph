// import * as vis from '../../assets/js/vis-network.min';
import { Network } from 'vis-network';
// import { DataSet } from 'vis-data';

const getNetwork = (element) => {
  // create an array with nodes
  const nodes = [
    { id: 1, label: 'Node 1' },
    { id: 2, label: 'Node 2' },
    { id: 3, label: 'Node 3' },
    { id: 4, label: 'Node 4' },
    { id: 5, label: 'Node 5' },
  ];

  // create an array with edges
  const edges = [
    { from: 1, to: 3 },
    { from: 1, to: 2 },
    { from: 2, to: 4 },
    { from: 2, to: 5 },
    { from: 3, to: 3 },
  ];

  // create a network
  // const container = document.getElementById('network');
  const data = {
    nodes,
    edges,
  };
  const options = {};
  return new Network(element, data, options);
};

const processData = () => {

};

export {
  getNetwork,
  processData,
};
