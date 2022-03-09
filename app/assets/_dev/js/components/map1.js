(function () {
  "use strict";
  window.oo = window.oo || {};

  window.oo.map = function (selection) {
    /**
     * Can be changed using the map.margin() method.
     */
    let margin = { top: 5, bottom: 20, left: 50, right: 5 };

    // The tooltip that appears when hovering over a bar or span.
    // Only need to create the element once, no matter how many charts are
    // on the page.
    var tooltip;
    if (document.getElementsByClassName("map-tooltip").length == 0) {
      tooltip = d3.select("body")
                    .append("div")
                    .classed("map-tooltip js-map-tooltip", true);
    } else {
      tooltip = d3.select(".map-tooltip");
    }

    var tooltipFormat = function (d) {
      // var text = "<strong>" + d.data.label + ":</strong> ";
      // if (chartType == "bar-stacked") {
      //   // Only need to show the group label if there are stacked bars.
      //   text += d.data.columns[groupKey]["label"] + ": ";
      // }
      // text += numberFormat(d.data.columns[groupKey]["value"]);
      // return text;
    };

    function onMouseover(d) {
      console.log('over', d.data)
      tooltip.html(tooltipFormat(d));
      tooltip.style("visibility", "visible");
    }

    function onMousemove(d) {

    }

    function onMouseout(d) {
      console.log('out', d)
      tooltip.style("visibility", "hidden");
    }

    /**
     * @param {object} selection The HTML elements to draw charts in.
     */
    function map(selection) {
      selection.each(function(data) {


        // TODO NEXT:
        // * Create a way to look up stuff from map_data by iso code
        // * Use that to color countries based on map_data properties
        // * Use that to create tooltips


        const container = d3.select(this);

        let width = parseInt(container.style('width'), 10);
        let height = parseInt(container.style('height'), 10);

        const svg = container.append("svg")
          .attr('viewBox', '0 0 '+width+ ' '+ height)
          .attr('preserveAspectRatio', "xMidYMid meet");

        const path = d3.geoPath();
        const projection = d3.geoMercator()
                            .translate([width/2, height/2])
                            .scale(120)
                            .center([0, 45]);

        const colorScale = d3.scaleThreshold()
          .domain([100000, 1000000, 10000000, 30000000, 100000000, 500000000])
          .range(d3.schemeBlues[7]);

        svg.append("g")
          .selectAll("path")
          .data(data.geojson.features)
          .join("path")
            // draw each country
            .attr("d", d3.geoPath()
              .projection(projection)
            )
            // set the color of each country
            .attr("fill", function (d) {
              console.log(d);
              // d.total = data.get(d.id) || 0;
              // return colorScale(d.total);
            })
            .on("mouseover", onMouseover)
            .on("mousemove", onMousemove)
            .on("mouseout", onMouseout)

      });
    }

    map.margin = function (value) {
      if (!arguments.length) return margin;
      margin = value;
      return map;
    };

    return map;
  };
})();
