function getNodePopup(node) {
    var result = "";
     result += "<table id='node-tooltip'>" +
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
//        node.group = node.is_ghost?"GhostGroup":node.name;
        node.label = node.abbrev;
        if (node.keys.length > 0) {
            var sep = node.keys_concat?"":","
            node.label += ": " + node.keys.map((k) => Object.values(k)[0]).join(sep);
        }
        node.title = getNodePopup(node);
        if (node.is_ghost) {
            node.color = "#DCDCDC";
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

var colors = [
	"#f0f8ff",
	"#efdecd",
	"#ffbf00",
	"#a4c639",
	"#cd9575",
	"#faebd7",
	"#8db600",
	"#fbceb1",
	"#7fffd4",
	"#e9d66b",
	"#ff9966",
	"#89cff0",
	"#f4c2c2",
	"#fae7b5",
	"#bcd4e6",
	"#f0ffff"
]

var shapes = [
    'square',
    'hexagon',
    'diamond',
    'triangle',
    'triangleDown',
    'ellipse',
    'dot',
    'box'
]

ghostGroup = {shape: 'star', color: '#DCDCDC'}

function randomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1) + min);
}

var Nodes, Edges, Network, shapeColorsIndex;

function getRandomGroupColorShape() {
    return {color: colors[randomInt(0, colors.length - 1)], shape: shapes[randomInt(0, shapes.length - 1)]}
}

function createGraph(data) {
    data = processData(data);

    Nodes = new vis.DataSet(data.nodes);
    Edges = new vis.DataSet(data.edges);

//    var groups = {},
//        groupNames = Array.from(new Set(data.nodes.map((n) => n.name)));
//
//    groupNames.forEach(function(gn, i) {
//        groups[gn] = getRandomGroupColorShape();
//    });
//    groups['GhostGroup'] = ghostGroup

    var container = document.getElementById('graph');

    var options = {
        interaction: {
            hover: true
        },
//        groups: groups
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
                success : function(result) {
                    createGraph(result.graph)
                    main.disableFilter();
                    main.disablePagination('next');
                    main.disablePagination('prev');
                    main.setPaginationText("");
                    main.setDescription("<strong>" + nodeName + "</strong>" + " (" + nodeId + ")");
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
//        if (Network.groups.groupsArray.indexOf(node.name) < 0) {
//            Network.groups.add(node.name, getRandomGroupColorShape());
//        }
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


