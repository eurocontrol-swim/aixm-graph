//+ function($) {
//    'use strict';
//
//    // UPLOAD CLASS DEFINITION
//    // ======================
//
//    var dropZone = document.getElementById('drop-zone');
//    var uploadForm = document.getElementById('js-upload-form');
//
//    var startUpload = function(files) {
//        console.log(files)
//    }
//
//    uploadForm.addEventListener('submit', function(e) {
//        var uploadFiles = document.getElementById('js-upload-files').files;
//        e.preventDefault()
//
//        startUpload(uploadFiles)
//    })
//
//    dropZone.ondrop = function(e) {
//        e.preventDefault();
//        this.className = 'upload-drop-zone';
//
//        startUpload(e.dataTransfer.files)
//    }
//
//    dropZone.ondragover = function() {
//        this.className = 'upload-drop-zone drop';
//        return false;
//    }
//
//    dropZone.ondragleave = function() {
//        this.className = 'upload-drop-zone';
//        return false;
//    }
//
//}(jQuery);

$(document).ready(function(){
    $.ajax({
        type: "POST",
        url: "/load_aixm",
        dataType : "json",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({filepath: "/media/alex/Data/dev/work/eurocontrol/aixm/samples/EA_AIP_DS_FULL_20170701.xml"}),
        success : function(result) {
            result.forEach(function(data) {
                featuresList.add(data);
            });
        }
    });
});

var data = {
  "nodes": [
    {
      "name": "Peter",
      "label": "Person",
      "id": 1
    },
    {
      "name": "Michael",
      "label": "Person",
      "id": 2
    },
    {
      "name": "Neo4j",
      "label": "Database",
      "id": 3
    },
    {
      "name": "Graph Database",
      "label": "Database",
      "id": 4
    }
  ],
  "links": [
    {
      "source": 1,
      "target": 2,
      "type": "KNOWS",
      "since": 2010
    },
    {
      "source": 1,
      "target": 3,
      "type": "FOUNDED"
    },
    {
      "source": 2,
      "target": 3,
      "type": "WORKS_ON"
    },
    {
      "source": 3,
      "target": 4,
      "type": "IS_A"
    }
  ]
}

var colors = d3.scaleOrdinal(d3.schemeCategory10);

var svg = d3.select("svg"),
    width = +svg.attr("width"),
    height = +svg.attr("height"),
    node,
    link;

svg.append('defs').append('marker')
    // .attrs({'id':'arrowhead',
    //     'viewBox':'-0 -5 10 10',
    //     'refX':13,
    //     'refY':0,
    //     'orient':'auto',
    //     'markerWidth':13,
    //     'markerHeight':13,
    //     'xoverflow':'visible'})
    .append('svg:path')
    .attr('d', 'M 0,-5 L 10 ,0 L 0,5')
    .attr('fill', '#999')
    .style('stroke','none');

var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function (d) {return d.id;}).distance(100).strength(1))
    .force("charge", d3.forceManyBody())
    .force("center", d3.forceCenter(width / 2, height / 2));

// d3.json(json, function (error, graph) {
//     if (error) throw error;
//     update(graph.links, graph.nodes);
// })
update(data.links, data.nodes);

function update(links, nodes) {
    link = svg.selectAll(".link")
        .data(links)
        .enter()
        .append("line")
        .attr("class", "link")
        .attr('marker-end','url(#arrowhead)')

    link.append("title")
        .text(function (d) {return d.type;});

    edgepaths = svg.selectAll(".edgepath")
        .data(links)
        .enter()
        .append('path')
        .attrs({
            'class': 'edgepath',
            'fill-opacity': 0,
            'stroke-opacity': 0,
            'id': function (d, i) {return 'edgepath' + i}
        })
        .style("pointer-events", "none");

    edgelabels = svg.selectAll(".edgelabel")
        .data(links)
        .enter()
        .append('text')
        .style("pointer-events", "none")
        .attrs({
            'class': 'edgelabel',
            'id': function (d, i) {return 'edgelabel' + i},
            'font-size': 10,
            'fill': '#aaa'
        });

    edgelabels.append('textPath')
        .attr('xlink:href', function (d, i) {return '#edgepath' + i})
        .style("text-anchor", "middle")
        .style("pointer-events", "none")
        .attr("startOffset", "50%")
        .text(function (d) {return d.type});

    node = svg.selectAll(".node")
        .data(nodes)
        .enter()
        .append("g")
        .attr("class", "node")
        .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                //.on("end", dragended)
        );

    node.append("circle")
//    .attr("points", "05,30 15,10 25,30")
         .attr("r", 5)
        // .attr("width", 50)
        // .attr("height", 100)
        .style("fill", function (d, i) {return colors(i);})

    node.append("title")
        .text(function (d) {return d.id;});

    node.append("text")
        .attr("dy", -3)
        .text(function (d) {return d.name+":"+d.label;});

    simulation
        .nodes(nodes)
        .on("tick", ticked);

    simulation.force("link")
        .links(links);
}

function ticked() {
    link
        .attr("x1", function (d) {return d.source.x;})
        .attr("y1", function (d) {return d.source.y;})
        .attr("x2", function (d) {return d.target.x;})
        .attr("y2", function (d) {return d.target.y;});

    node
        .attr("transform", function (d) {return "translate(" + d.x + ", " + d.y + ")";});

    edgepaths.attr('d', function (d) {
        return 'M ' + d.source.x + ' ' + d.source.y + ' L ' + d.target.x + ' ' + d.target.y;
    });

    edgelabels.attr('transform', function (d) {
        if (d.target.x < d.source.x) {
            var bbox = this.getBBox();

            rx = bbox.x + bbox.width / 2;
            ry = bbox.y + bbox.height / 2;
            return 'rotate(180 ' + rx + ' ' + ry + ')';
        }
        else {
            return 'rotate(0)';
        }
    });
}

function dragstarted(d) {
    if (!d3.event.active) simulation.alphaTarget(0.3).restart()
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
}
