import { Network } from 'vis-network';

const ghostNodeColor = '#FF0000';
const ghostNodeShape = 'star';

const getNodePopup = (node) => {
  let result = `<table id="node-tooltip" data-node-id="${node.id}">`
    + '<tr style="border-bottom: 1px solid black;">'
      + `<td style="padding: 0px;"><strong>${node.name}</strong></td>`
      + '<td style="padding: 0px 10px;"></td>'
    + '</tr>'
    + '<tr>'
      + '<td style="padding: 0px;"><strong>UUID</strong></td>'
      + `<td style="padding: 0px 10px;">${node.id} (Ctrl-C to copy)</td>`
    + '</tr>';

  node.fields.forEach((field) => {
    const name = Object.keys(field)[0];
    const value = Object.values(field)[0];
    result += '<tr>'
        + `<td style="padding: 0px;"><strong>${name}</strong></td>`
        + `<td style="padding: 0px 10px;">${value}</td>`
    + '</tr>';
  });

  result += '<tr>'
      + '<td style="padding: 0px;"><strong>Num of associations</strong></td>'
      + `<td style="padding: 0px 10px">${node.assoc_count}</td>`
  + '</tr>';

  result += '</table>';

  return result;
};

const getEnhancedNodeClosure = (edges) => ((origNode) => {
  const nodeEdges = edges.filter((e) => e.source === origNode.id || e.target === origNode.id);
  let label = origNode.assoc_count > nodeEdges.length ? `[+] ${origNode.abbrev}` : origNode.abbrev;

  if (origNode.fields.length > 0) {
    const sep = origNode.fields_concat ? '' : ',';
    const fields = origNode.fields.map((k) => Object.values(k)[0]).join(sep);
    label += `: ${fields}`;
  }

  return {
    id: origNode.id,
    label,
    associationsNum: origNode.assoc_count,
    title: getNodePopup(origNode),
    color: origNode.is_ghost ? ghostNodeColor : origNode.color,
    shape: origNode.is_ghost ? ghostNodeShape : origNode.shape,
  };
});


const getEnhancedEdge = (origEdge) => ({
  from: origEdge.source,
  to: origEdge.target,
  label: origEdge.name,
  dashes: origEdge.is_broken,
});

const createNetwork = (element, origNodes, origEdges) => {
  const getEnhancedNode = getEnhancedNodeClosure(origEdges);

  const data = {
    nodes: origNodes.map((node) => getEnhancedNode(node)),
    edges: origEdges.map((edge) => getEnhancedEdge(edge)),
  };

  const options = {
    interaction: {
      hover: true,
    },
  };

  return new Network(element, data, options);
};

const updateNetwork = (network) => {
  console.log(network);
};

export {
  createNetwork,
  updateNetwork,
};
