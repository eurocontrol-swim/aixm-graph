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
        node.group = node.is_ghost?"GhostGroup":node.name;
        node.label = node.abbrev;
        if (node.keys.length > 0) {
            var sep = node.keys_concat?"":","
            node.label += ": " + node.keys.map((k) => Object.values(k)[0]).join(sep);
        }
        node.title = getNodePopup(node);
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
	"#5d8aa8",
	"#f0f8ff",
	"#e32636",
	"#efdecd",
	"#e52b50",
	"#ffbf00",
	"#ff033e",
	"#9966cc",
	"#a4c639",
	"#f2f3f4",
	"#cd9575",
	"#915c83",
	"#faebd7",
	"#008000",
	"#8db600",
	"#fbceb1",
	"#00ffff",
	"#7fffd4",
	"#4b5320",
	"#e9d66b",
	"#b2beb5",
	"#87a96b",
	"#ff9966",
	"#a52a2a",
	"#fdee00",
	"#6e7f80",
	"#ff2052",
	"#007fff",
	"#f0ffff",
	"#89cff0",
	"#a1caf1",
	"#f4c2c2",
	"#21abcd",
	"#fae7b5",
	"#ffe135",
	"#848482",
	"#98777b",
	"#bcd4e6",
	"#9f8170"
]

var shapes = [
//    'circle',
//    'star',
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

    var groups = {},
        groupNames = Array.from(new Set(data.nodes.map((n) => n.name)));

    groupNames.forEach(function(gn, i) {
        groups[gn] = getRandomGroupColorShape();
    });
    groups['GhostGroup'] = ghostGroup

    var container = document.getElementById('graph');

    var options = {
        interaction: {
            hover: true
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
        if (Network.groups.groupsArray.indexOf(node.name) < 0) {
            Network.groups.add(node.name, getRandomGroupColorShape());
        }
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


