// $( document ).ready(function() {

var svg = d3.select("svg"),
    width = +svg.attr("width"),
    height = +svg.attr("height");

var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function (d) {
        return d.id;
    }))
    .force("charge", d3.forceManyBody())
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("x", d3.forceX())
    .force("y", d3.forceY());;

d3.json("force/force.json", function (error, graph) {
    if (error) throw error;

    var link = svg.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(graph.links)
        .enter().append("line");

    var node = svg.append("g")
        .attr("class", "nodes")
        .selectAll("circle")
        .data(graph.nodes)
        .enter().append("circle")
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));

    var node_attributes = node
        .attr("r", 5)
        .style("fill", function(d) {return d.color})
        .attr('text', function(d) {return d.author_name})
        .attr("transform", d => `translate(${0})`);

    node.append("title")
        .text(function (d) {
            return d.author_name;
        });

    node.append("text")
      .attr("x", 8)
      .attr("y", "0.31em")
      .text(d => d.author_name)

    node.on("click", display_author_infos);

    simulation
        .nodes(graph.nodes)
        .on("tick", ticked);

    simulation.force("link")
        .links(graph.links);

    function ticked() {
        link
            .attr("x1", function (d) {
                return d.source.x;
            })
            .attr("y1", function (d) {
                return d.source.y;
            })
            .attr("x2", function (d) {
                return d.target.x;
            })
            .attr("y2", function (d) {
                return d.target.y;
            });

        node
            .attr("cx", function (d) {
                return d.x;
            })
            .attr("cy", function (d) {
                return d.y;
            });
    }

//     svg.call(d3.zoom()
//       .extent([[0, 0], [width, height]])
//       .scaleExtent([1, 8])
//       .on("zoom", zoomed));

//       function zoomed({transform}) {
//         svg.attr("transform", transform);
//       }
});

function dragstarted(d) {
    if (!d3.event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
}

function dragended(d) {
    if (!d3.event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

var cur_auth;

function display_author_infos(d){
    console.log(d)
    cur_auth=d.id_author;
    document.getElementById('author_name').innerHTML=d.author_name;
    console.log(document.getElementById('author_name'))
    if(d.publications.length>1){
        document.getElementById('publication_label').innerHTML="Publications:"
    } else {
        document.getElementById('publication_label').innerHTML="Publication:"
    }
    var ul = document.getElementById('publication_list');
    while (ul.hasChildNodes()) {  
        ul.removeChild(ul.firstChild);
    }
    for (i=0; i<=d.publications.length; i++){
        var li = document.createElement("li");
        li.appendChild(document.createTextNode(d.publications[i][0] + "(" + d.publications[i][1] + ")"));
        ul.appendChild(li);
    }
}

var x = document.getElementById('year');
httpRequest = new XMLHttpRequest();
httpRequest.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
        response = httpRequest.responseText
        year = []
        year_number = ''
        for (letter=0; letter<response.length; letter++){
            // console.log(response[letter])
            if(response[letter] != "," && response[letter] != "]"){
                if (response[letter] != "[" && response[letter] != " "){
                    year_number=year_number.concat(response[letter])
                }
            } else {
                year.push(year_number);
                year_number = ''
            }
        }
        for (i=0; i<year.length; i++){
            console.log(year[i])
            var option = document.createElement("option");
            option.text = year[i];
            option.value = year[i];
            x.add(option, x[1]);
        }
    }
};
httpRequest.open('GET', 'http://localhost:10546/get_year_list', true);
httpRequest.send();

var prediction = document.getElementById('prediction_chart');
httpRequest = new XMLHttpRequest();
httpRequest.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
        response = httpRequest.responseText
        conf = []
        conf_label = ''
        for (letter=0; letter<response.length; letter++){
            // console.log(response[letter])
            if(response[letter] != "," && response[letter] != "]"){
                if (response[letter] != "[" && response[letter] != " " && response[letter] != "'"){
                    conf_label=conf_label.concat(response[letter])
                }
            } else {
                conf.push(conf_label);
                conf_label = ''
            }
        }
        for (i=0; i<conf.length; i++){
            var option = document.createElement("option");
            option.text = conf[i];
            option.value = conf[i];
            conf_item.add(option, conf_item[1]);
        }
    }
};
httpRequest_conf.open('GET', 'http://localhost:10546/get_conf_list', true);
httpRequest_conf.send();

function send_data(){
    var xhttp = new XMLHttpRequest();
    var path = "http://localhost:10546/get_graph"
    if(document.getElementById('conf').value!=""){
        if(path=="http://localhost:10546/get_graph")
            path += "?";
        else {
            path += "&";
        }
        path += "publication_conf="+document.getElementById('conf').value;
    }
    if(document.getElementById('year').value!=""){
        if(path=="http://localhost:10546/get_graph")
            path += "?";
        else {
            path += "&";
        }
        path += "publication_year="+document.getElementById('year').value;
    }
    if(document.getElementById('start_date').value!=""){
        if(path=="http://localhost:10546/get_graph")
            path += "?";
        else {
            path += "&";
        }
        path += "publication_start_date="+document.getElementById('start_date').value;
    }
    if(document.getElementById('end_date').value!=""){
        if(path=="http://localhost:10546/get_graph")
            path += "?";
        else {
            path += "&";
        }
        path += "publication_end_date="+document.getElementById('end_date').value;
    }
    // console.log(path)
    // xhttp.open("GET", path);
    // xhttp.send();
    // window.location.assign(path)
    window.location.href = path
}

function get_sub_graph(){
    author = cur_auth;
    // window.location.assign('http://localhost:10546/get_sub_graph_analysis?author_id='+author)
    window.location.href = 'http://localhost:10546/get_sub_graph_analysis?author_id='+author
    // if (author != ""){
    //     console.log(author)
    //     httpRequest_sub_graph = new XMLHttpRequest();
    //     httpRequest_sub_graph.onreadystatechange = function() {
    //         if (this.readyState == 4 && this.status == 200) {
    //             window.location.load(httpRequest_sub_graph.responseText)
    //         }
    //     };
    //     httpRequest_sub_graph.open('GET', 'http://localhost:10546/get_sub_graph_analysis?author_id='+author, true);
    //     httpRequest_sub_graph.send();
    // } else {
    //     alert('select an author');
    // }
}
// });