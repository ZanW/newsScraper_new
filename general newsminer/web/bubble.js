var showChart = function (url) {
    const host = "http://localhost",
        port = 8080;

    var Title = function (title, weight) {
        this.text = title;
        this.weight = weight;
    }


    $.get(url, function (data) {
        // for(var i = 0;i<20;i++){
        //     words[i]={title:data[i]["Title"],weight:data[i]["Similatiry_Fre"]};
        // }


        console.log(data)

        // console.log([{a:1,b:2},6,9])
        var width = 1000,
            height = 600;

        var svg = d3
            .select("#chart")
            .append("svg")
            .attr("xmlns","http://www.w3.org/2000/svg")
            .attr("height", height)
            .attr("width", width)

        var nodes = d3.select("svg").selectAll(".node");

        console.log(nodes.data(data))
        var simulation = d3.forceSimulation()
            .force("x", d3.forceX(width / 2).strength(0.05))
            .force("y", d3.forceY(height / 2).strength(0.05))
            .force("collide", d3.forceCollide(function (d) {
                return radiusScale(d.Similatiry_Fre) + 1
            }))
        // .force("collide", d3.forceCollide(function (d) {
        //     return radiusScale(d.count) + 1
        // }))


        var maxWeight=0
        var minWeight=9999999
        for(var o in data){
            maxWeight=Math.max(data[o].Similatiry_Fre,maxWeight)
            minWeight=Math.min(data[o].Similatiry_Fre,minWeight)
        }


        var radiusScale = d3.scaleSqrt().domain([minWeight, maxWeight]).range([50, 120])




        // console.log(data.forEach(function (t) { t.Similatiry_Fre }))

        // d3.queue()
        //     .defer(Array, words)
        //     .await(start);
        // d3.queue()
        //     .defer(d3.csv, "top_aesop.csv")
        //     .await(start);

        start(data)

        console.log(data)

        function start(datapoints) {
            console.log(datapoints)
            createNode(datapoints)
            var simu = simulation
                .nodes(datapoints)
                .on('tick', tick)
            // createLabel(datapoints)

        }

        function createNode(datapoints) {
            var selectColor = function (index) {
                switch (index) {
                    case 0:
                        return "rgba(237,70,47,0.8)";
                    case 1:
                        return "rgba(221,116,43,0.8)";
                    case 2:
                        return "rgba(231,225,46,0.8)";
                    case 3:
                        return "rgba(197,241,71,0.8)";
                    case 4:
                        return "rgba(143,236,143,0.8)";
                    default:
                        return "rgba(30,143,251,0.8)";
                }
            }
            nodes
                .data(datapoints)
                .enter()
                .append("g")
                .attr("class", "node")
            // .on("click", function (d) {
            //     console.log(d);
            // })

            svg.selectAll(".node")
                .data(datapoints)
                .append("circle")
                .attr("r", function (d) {
                    return radiusScale(d.Similatiry_Fre)
                })
                // .attr("fill", "lightblue")
                .attr("fill", function (d) {
                    return selectColor(data.indexOf(d))
                })


            let showtext = svg.append("text")
                .text("")

            svg.selectAll("circle")
            // .attr("fill","lightblue")
                .on("mouseover", function (d) {
                    d3.select(this)
                        .transition()
                        .duration(200)
                        .attr("r", d3.select(this).attr("r") * 1.1)
                    // .attr("fill","lightblue")
                    // showtext.attr("x",function () {
                    //     return xScale
                    // })

                })
                .on("mouseout", function (d) {
                    d3.select(this)
                        .transition()
                        .duration(200)
                        .attr("r", function (d) {
                            return radiusScale(d.Similatiry_Fre)
                        })

                })
                .on("click", function (d) {
                    $("#title")
                        .html("<p style='font-size: 30px;font-weight: bold'>" + d.Title + "<p>")
                })

            // svg.selectAll(".node")
            //     .data(datapoints)
            //     .append("foreignObject")
            //     .attr("class","text")
            //     .attr("width",function (d) {return radiusScale(d.Similatiry_Fre)*2/Math.sqrt(2)})
            //     .attr("height",function (d) {return radiusScale(d.Similatiry_Fre)*2/Math.sqrt(2)})
            //     .attr("x",function (d) {return -radiusScale(d.Similatiry_Fre)/Math.sqrt(2)})
            //     .attr("y",function (d) {return -radiusScale(d.Similatiry_Fre)/Math.sqrt(2)})

            svg.selectAll(".node")
                .selectAll("text")
                .append("text")


            svg.selectAll(".node")
                .append("text")
                .attr("text-anchor", "middle")
                // .attr("font-size","20")
                .attr("style", "font:18px Arial")
                .append("tspan")
                .text(function (d) {
                    let text = d.Title.toString().split(" ")
                    return text[0] + " " + text[1] + "..."
                })

            svg.selectAll(".node")
                .append("text")
                .attr("text-anchor", "middle")
                .append("tspan")
                .attr("dy", "1em")
                .text(function (d) {
                    return d.Similatiry_Fre
                })


            if (datapoints[0]["Tstamp"]) {
                $("#table_head").append("<th style='width: 100px;'>time</th>")

                datapoints.forEach(function (respose) {
                    $("#table_body").append(
                        "<tr>" +
                        "<td>" + "<a href=" + respose["URL"] + ">" + respose["Title"] + "</a></td>" +
                        "<td>" + respose["Similatiry_Fre"] + "</td>" +
                        "<td>" + respose["Tstamp"] + "</td>" +
                        "</tr>")
                })
            } else {

                datapoints.forEach(function (respose) {
                    $("#table_body").append(
                        "<tr>" +
                        "<td>" + "<a href=" + respose["URL"] + ">" + respose["Title"] + "</a></td>" +
                        "<td>" + respose["Similatiry_Fre"] + "</td>" +
                        "</tr>")
                })

            }



            // svg.selectAll(".text")
            //     .append("div")
            //     .append("p")
            //     .text(function (d) {
            //         console.log(d.Title.toString().split(" "))
            //     })

        }


        // function createLabel(datapoints) {
        //     svg.selectAll(".node")
        //         .data(datapoints)
        //         .enter()
        //         .append("text")
        // }

        function tick() {
            svg.selectAll(".node").attr("transform", function (d) {
                return "translate(" + d.x + "," + d.y + ")";
            })
        }

    })

}