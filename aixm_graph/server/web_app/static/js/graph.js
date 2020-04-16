function getNodePopup(node) {
    var result = "";
     result += "<table id='node-tooltip' data-node-id=" + node.id + ">" +
        "<tr style='border-bottom: 1px solid black;'>" +
            "<td style='padding: 0px;'><strong>" + node.name + "</strong></td>" +
            "<td style='padding: 0px 10px;'></td>" +
        "</tr>" +
        "<tr>" +
            "<td style='padding: 0px;'><strong>UUID</strong></td>" +
            "<td style='padding: 0px 10px;'>" + node.id + " (Ctrl-C to copy)</td>" +
        "</tr>";

     node.fields.forEach(function(field) {
        var name = Object.keys(field)[0];
        var value = Object.values(field)[0];
        result += "<tr>" +
            "<td style='padding: 0px;'><strong>" + name + "</strong></td>" +
            "<td style='padding: 0px 10px;'>" + value + "</td>" +
        "</tr>";
     });

     result += "<tr>" +
         "<td style='padding: 0px;'><strong>Num of associations</strong></td>" +
         "<td style='padding: 0px 10px'>" + node.associationsNum + "</td>" +
     "</tr>";

     result += "</table>"

     return result;
}

function processData(data) {
    data.nodes.forEach(function(node) {
        var currentLinks = data.edges.filter((e) => e.source == node.id || e.target == node.id)

        node.label = node.assoc_count > currentLinks.length ? "[+] " + node.abbrev : node.abbrev;
        node.associationsNum = node.assoc_count;

        if (node.fields.length > 0) {
            var sep = node.fields_concat?"":","
            node.label += ": " + node.fields.map((k) => Object.values(k)[0]).join(sep);
        }
        node.title = getNodePopup(node);
        if (node.is_ghost) {
            node.color = "#FF0000";
            node.shape = "star";
        }
    });

    data.edges.forEach(function(edge) {
        edge.from = edge.source;
        edge.to = edge.target;
        edge.label = edge.name;
        if (edge.is_broken) {
            edge.dashes = true;
        }
    });

    return data;
}


var Nodes, Edges, Network, shapeColorsIndex;

function createGraph(data) {
    data = processData(data);

    Nodes = new vis.DataSet(data.nodes);
    Edges = new vis.DataSet(data.edges);

    var container = document.getElementById('graph');
    var options = {
        interaction: {
            hover: true
        }
    };

    Network = new vis.Network(container, {nodes: Nodes, edges: Edges}, options);

    Network.on("oncontext", function (params) {
//        params.event = "[original event]";
        params.event.preventDefault();

        var nodeId = Network.getNodeAt(params.pointer.DOM);
        var nodeName = Nodes.get(nodeId).name;

        $.ajax({
            type: "GET",
            url: "/datasets/" + Sidenav.datasetId + "/features/" + nodeId + "/graph",
            dataType : "json",
            contentType: "application/json; charset=utf-8",
            success : function(response) {
                createGraph(response.data.graph)

                Main.createAssociations(response.data.graph.nodes, nodeName);
                Main.disableFilter();
                Main.disablePagination('next');
                Main.disablePagination('prev');
                Main.setPaginationText("");
                Main.setDescription("<strong>" + nodeName + "</strong>" + " (" + nodeId + ")");
            },
            error: function(response) {
                console.log(response.responseJSON.error);
                showError('Failed to get the graph for feature ' + nodeName + ' ' + nodeId);
            }
        });

        Main.showGraphLoader();
    });

    Network.on("click", function (params) {
        if (params.nodes.length > 0) {
            var nodeId = params.nodes[0];

            $.ajax({
                type: "GET",
                url: "/datasets/" + Sidenav.datasetId + "/features/" + nodeId + "/graph",
                dataType : "json",
                contentType: "application/json; charset=utf-8",
                success : function(response) {
                    updateGraph(response.data.graph)
                },
                error: function(response) {
                    console.log(response.responseJSON.error);
                    showError('Failed to expand the graph.');
                }
            });
        }
    });


}

function updateGraph(data) {
    data = processData(data);

    data.nodes.forEach(function(node) {
        if (!nodeExists(node)) {
            Nodes.add(node);
        }
    });

    data.edges.forEach(function(edge) {
        if (!edgeExists(edge)) {
            Edges.add(edge);
        }
    });

    // update labels of existing nodes
    Network.body.nodeIndices.forEach(function(index) {
        node = Network.body.nodes[index];
        if ( node.options.assoc_count == node.edges.length && node.options.label.startsWith("[+] ")) {
            node.options.label = node.options.label.slice(4);
        }
    });

}


function nodeExists(node) {
    return Nodes.getIds().indexOf(node.id) >= 0;
}

function edgeExists(edge) {
    edgeIds = Edges.getIds()

    for (var i = 0; i < edgeIds.length; i++ ) {
        var e = Edges.get(edgeIds[i]);

        if ((e.to == edge.to && e.from == edge.from) || (e.to == edge.from && e.from == edge.to)) {
            return true;
        }
    }
    return false;
}

function getBranchIds(rootNodeId, branchIds, excludedNodeIds) {
    branchIds = branchIds || [];

    var self = this,
        node = Network.body.nodes[rootNodeId];

    if (node == undefined) {
        return branchIds;
    }

    node.edges.forEach(function(edge) {
        var targetNode = edge.to;
        if (excludedNodeIds.concat(node.id).indexOf(targetNode.id) < 0) {
            branchIds.push(targetNode.id);

            if (targetNode.edges) {
                self.getBranchIds(targetNode.id, branchIds, excludedNodeIds);
            }
        }
    });

    return branchIds;
}
