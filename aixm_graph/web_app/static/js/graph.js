function getNodePopup(node) {
    var result = "";
     result += "<table id='node-tooltip' data-node-id=" + node.id + ">" +
        "<tr style='border-bottom: 1px solid black;'>" +
            "<td style='padding: 0px;'><strong>" + node.name + "</strong></td>" +
            "<td style='padding: 0px;'></td>" +
        "</tr>" +
        "<tr>" +
            "<td style='padding: 0px;'><strong>UUID</strong></td>" +
            "<td style='padding: 0px;'>" + node.id + "</td>" +
        "</tr>";

     node.keys.forEach(function(key) {
        var name = Object.keys(key)[0];
        var value = Object.values(key)[0];
        result += "<tr>" +
            "<td style='padding: 0px;'><strong>" + name + "</strong></td>" +
            "<td style='padding: 0px;'>" + value + "</td>" +
        "</tr>";
     });

     result += "</table>"

     return result;
}

function processData(data) {
    data.nodes.forEach(function(node) {
        var currentLinks = data.edges.filter((e) => e.source == node.id || e.target == node.id)

        node.label = node.links_count > currentLinks.length ? "[+] " + node.abbrev : node.abbrev;

        if (node.keys.length > 0) {
            var sep = node.keys_concat?"":","
            node.label += ": " + node.keys.map((k) => Object.values(k)[0]).join(sep);
        }
        node.title = getNodePopup(node);
        if (node.is_ghost) {
            node.color = "#FF0000";
            node.shape = "star";
        }
        else {
            node.color = config[node.name].color;
            node.shape = config[node.name].shape;
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

    Network.on("doubleClick", function (params) {
        if (params.nodes.length > 0) {
            var nodeId = params.nodes[0];
            var nodeName = Nodes.get(nodeId).name;

            $.ajax({
                type: "GET",
                url: "/feature/" + nodeId + "/graph",
                dataType : "json",
                contentType: "application/json; charset=utf-8",
                success : function(response) {
                    createGraph(response.data.graph)
                    main.disableFilter();
                    main.disablePagination('next');
                    main.disablePagination('prev');
                    main.setPaginationText("");
                    main.setDescription("<strong>" + nodeName + "</strong>" + " (" + nodeId + ")");
                },
                error: function(response) {
                    console.log(response.responseJSON.error);
                    showError('Failed to get the graph for feature ' + nodeName + ' ' + nodeId);
                }
            });
        }
    });

    Network.on("click", function (params) {
        if (params.nodes.length > 0) {
            var nodeId = params.nodes[0];

            $.ajax({
                type: "GET",
                url: "/feature/" + nodeId + "/graph",
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

    $(document).keydown(function(e){
        if(e.which === 67 && e.ctrlKey){
            var tooltip = $("#node-tooltip")[0];
            if (tooltip) {
                var nodeId = tooltip.getAttribute('data-node-id');
                copyToClipboard(nodeId);
            }
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


