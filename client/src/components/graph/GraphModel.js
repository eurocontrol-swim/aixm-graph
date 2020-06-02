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

import { Network } from 'vis-network';

const ghostNodeColor = '#FF0000';
const ghostNodeShape = 'star';

export default class GraphModel {
  constructor(element, data, config) {
    this.element = element;
    this.data = data;
    this.config = config;

    this.network = this.createNetwork(element, data, config);
  }

  createNetwork = (element, origData, config) => {
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

    const data = GraphModel.getEnhancedData(origData, config);

    return new Network(element, data, options);
  };

  on = (eventType, callback) => {
    this.network.on(eventType, callback);
  };

  update = (origData) => {
    const data = GraphModel.getEnhancedData(origData, this.config);

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

  static getNodePopup = (node) => {
    let result = `<table id="node-tooltip" data-node-id="${node.id}">`
      + '<tr style="border-bottom: 1px solid black;">'
        + `<td style="padding: 0px;"><strong>${node.name}</strong></td>`
        + '<td style="padding: 0px 10px;"></td>'
      + '</tr>'
      + '<tr>'
        + '<td style="padding: 0px;"><strong>ID</strong></td>'
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

  static getEnhancedNodeClosure = (edges) => ((origNode, config) => {
    const nodeEdges = edges.filter((e) => e.source === origNode.id || e.target === origNode.id);

    const abbrev = (config !== undefined) ? config.abbrev : origNode.name;

    let label = origNode.assoc_count > nodeEdges.length ? `[+] ${abbrev}` : abbrev;

    if (origNode.fields.length > 0) {
      const sep = config.fields.concat ? '' : ',';
      const fields = origNode.fields.map((k) => Object.values(k)[0]).join(sep);
      label += `: ${fields}`;
    }

    return {
      id: origNode.id,
      name: origNode.name,
      label,
      associationsNum: origNode.assoc_count,
      title: GraphModel.getNodePopup(origNode),
      color: origNode.is_ghost ? ghostNodeColor : config.color,
      shape: origNode.is_ghost ? ghostNodeShape : config.shape,
    };
  });

  static getEnhancedEdge = (origEdge) => {
    const directions = {
      target: 'to',
      source: 'from',
    };

    const enhanced = {
      from: origEdge.source,
      to: origEdge.target,
      label: origEdge.name,
      dashes: origEdge.is_broken,
    };

    if (origEdge.direction !== null) {
      enhanced.arrows = directions[origEdge.direction];
    }

    return enhanced;
  }

  static getEnhancedData = (origData, config) => {
    const getEnhancedNode = GraphModel.getEnhancedNodeClosure(origData.edges);

    return {
      nodes: origData.nodes.map((node) => getEnhancedNode(node, config[node.name])),
      edges: origData.edges.map((edge) => GraphModel.getEnhancedEdge(edge)),
    };
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
