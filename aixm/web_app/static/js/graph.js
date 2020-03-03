function getNodePopup(node) {
    var result = "";
     result += "<table>" +
        "<tr style='border-bottom: 1px solid black'>" +
            "<td><strong>" + node.name + "</strong></td>" +
            "<td></td>" +
        "</tr>" +
        "<tr>" +
            "<td><strong>UUID</strong></td>" +
            "<td>" + node.id + "</td>" +
        "</tr>";

     node.keys.forEach(function(key) {
        var name = Object.keys(key)[0];
        var value = Object.values(key)[0];
        result += "<tr>" +
            "<td><strong>" + name + "</strong></td>" +
            "<td>" + value + "</td>" +
        "</tr>";
     });

     result += "</table>"

     return result;
}
//                <td>` + node.id.slice(0, 8) + `</td>

function processData(data) {
    data.nodes.forEach(function(node) {
        node.group = node.name;
        node.label = node.abbrev;
        if (node.keys.length > 0) {
            node.label += ": " + (node.keys.map((k) => Object.values(k)[0])).join(",");
        }
        node.title = getNodePopup(node);
    });

    data.edges.forEach(function(edge) {
        edge.from = edge.source;
        edge.to = edge.target;
    });

    return data;
}

var shapeColors = [
    {shape: 'box', color:'#97C2FC'},
//    {shape: 'circle', color:'#FFFF00'},
    {shape: 'diamond', color:'#FB7E81'},
    {shape: 'dot', size: 10, color:'#7BE141'},
    {shape: 'ellipse', color:'#7fdae8'},
//    {shape: 'star', color:'#C2FABC'},
    {shape: 'triangle', color:'#FFA807'},
    {shape: 'triangleDown', color:'#6E6EFD'}
];

var Nodes, Edges, Network;

function createGraph(data) {
    data = processData(data);

    Nodes = new vis.DataSet(data.nodes);
    Edges = new vis.DataSet(data.edges);

    var groups = {},
        groupNames = Array.from(new Set(data.nodes.map((n) => n.name)));

    groupNames.forEach(function(gn, i) {
        groups[gn] = shapeColors[i % shapeColors.length]
    });

    var container = document.getElementById('graph');

    var options = {
        interaction: {
            hover: true,
            navigationButtons: true
        },
        groups: groups
    };

    Network = new vis.Network(container, {nodes: Nodes, edges: Edges}, options);

    Network.on("doubleClick", function (params) {
        if (params.nodes.length > 0) {
            var nodeId = params.nodes[0]

            $.ajax({
                type: "GET",
                url: "/feature/" + nodeId + "/graph",
                dataType : "json",
                contentType: "application/json; charset=utf-8",
                success : function(result) {
                    createGraph(result.graph)
                }
            });
        }
    });

    Network.on("click", function (params) {
        if (params.nodes.length > 0) {
            var nodeId = params.nodes[0]

            $.ajax({
                type: "GET",
                url: "/feature/" + nodeId + "/graph",
                dataType : "json",
                contentType: "application/json; charset=utf-8",
                success : function(result) {
                    updateGraph(result.graph)
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


