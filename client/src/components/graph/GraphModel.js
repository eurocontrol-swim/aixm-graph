import { Network } from 'vis-network';

const ghostNodeColor = '#FF0000';
const ghostNodeShape = 'star';

export default class GraphModel {
  constructor(element, data) {
    this.element = element;
    this.data = data;

    this.network = this.createNetwork(element, data);
  }

  createNetwork = (element, origData) => {
    const options = {
      interaction: {
        hover: true,
      },
      nodes: {
        shapeProperties: {
          interpolation: false,
        },
      },
      layout: {
        improvedLayout: false,
      },
      physics: {
        stabilization: false,
      },
    };

    const data = GraphModel.getEnhancedData(origData);

    return new Network(element, data, options);
  };

  on = (eventType, callback) => {
    this.network.on(eventType, callback);
  };

  update = (origData) => {
    const data = GraphModel.getEnhancedData(origData);

    data.nodes.forEach((node) => {
      this.addNode(node);
    });

    data.edges.forEach((edge) => {
      this.addEdge(edge);
    });

    // update labels of existing nodes
    this.network.body.nodeIndices.forEach((index) => {
      const node = this.network.body.nodes[index];
      if (node.options.associationsNum === node.edges.length
          && node.options.label.startsWith('[+] ')) {
        node.options.label = node.options.label.slice(4);
      }
    });
  };

  getNodes = () => this.network.body.data.nodes;

  getEdges = () => this.network.body.data.edges;

  addNode = (node) => {
    if (!this.nodeExists(node)) {
      this.getNodes().add(node);
    }
  }

  removeNodeById = (nodeId) => {
    this.getNodes().remove(nodeId);
  };

  addEdge = (edge) => {
    if (!this.edgeExists(edge)) {
      this.getEdges().add(edge);
    }
  }

  nodeExists = (node) => this.network.body.nodeIndices.indexOf(node.id) >= 0;

  edgeExists = (edge) => {
    const edgeIds = this.getEdges().getIds();

    for (let i = 0; i < edgeIds.length; i += 1) {
      const e = this.getEdges().get(edgeIds[i]);

      if ((e.to === edge.to && e.from === edge.from)
          || (e.to === edge.from && e.from === edge.to)) {
        return true;
      }
    }
    return false;
  };

  getNodeIdAtPointer = (pointer) => this.network.getNodeAt(pointer);

  getNodeById = (nodeId) => this.getNodes().get(nodeId);

  // getNodeIdsByName = (name) => this.getNodes()
  static getNodePopup = (node) => {
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

  static getEnhancedNodeClosure = (edges) => ((origNode) => {
    const nodeEdges = edges.filter((e) => e.source === origNode.id || e.target === origNode.id);

    let label = origNode.assoc_count > nodeEdges.length ? `[+] ${origNode.abbrev}` : origNode.abbrev;

    if (origNode.fields.length > 0) {
      const sep = origNode.fields_concat ? '' : ',';
      const fields = origNode.fields.map((k) => Object.values(k)[0]).join(sep);
      label += `: ${fields}`;
    }

    return {
      id: origNode.id,
      name: origNode.name,
      label,
      associationsNum: origNode.assoc_count,
      title: GraphModel.getNodePopup(origNode),
      color: origNode.is_ghost ? ghostNodeColor : origNode.color,
      shape: origNode.is_ghost ? ghostNodeShape : origNode.shape,
    };
  });

  static getEnhancedEdge = (origEdge) => ({
    from: origEdge.source,
    to: origEdge.target,
    label: origEdge.name,
    dashes: origEdge.is_broken,
  });

  static getEnhancedData = (origData) => {
    const getEnhancedNode = GraphModel.getEnhancedNodeClosure(origData.edges);
    const nodes = origData.nodes.map((node) => getEnhancedNode(node));
    const edges = origData.edges.map((edge) => GraphModel.getEnhancedEdge(edge));

    return { nodes, edges };
  };

  getBranchIds = (rootNodeId, incomingBranchIds, excludedNodeIds) => {
    const branchIds = incomingBranchIds || [];
    const self = this;
    const node = this.network.body.nodes[rootNodeId];

    if (node === undefined) {
      return branchIds;
    }

    node.edges.forEach((edge) => {
      const targetNode = edge.to;
      if (excludedNodeIds.concat(node.id).indexOf(targetNode.id) < 0) {
        branchIds.push(targetNode.id);

        if (targetNode.edges) {
          self.getBranchIds(targetNode.id, branchIds, excludedNodeIds);
        }
      }
    });

    return branchIds;
  };
}