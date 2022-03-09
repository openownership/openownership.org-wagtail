// The selector we use to find the element into which we put the map:
const mapSelector = ".js-map";

const worldMap = (function () {
  "use strict";

  var publicAPIs = {};

  var mapData = {};
  var container = null;
  var svg = null;
  var width = null;
  var height = null;
  var path = null;
  var tooltip = null;

  /**
   * Call this to initialise everything.
   * @param {object} options Should have:
   *  mapSelector: string, the selector of the element into which we put the map
   *  mapData: array of objects, one per country with OO data.
   *  geojsonPath: path to geojson file to draw the map with.
   */
  publicAPIs.init = function (options) {

    container = d3.select(options.mapSelector);
    initMapData(options.mapData);
    initMap();
    initTooltip();
    initListeners();


    d3.json(options.geojsonPath).then(function (geojsonData) {
      generateMap(geojsonData);
    });
  };

  // PRIVATE METHODS

  /**
   * Take the map data array from the back end and transform it into an object
   * keyed by the iso2 values.
   * Sets the mapData object.
   * @param {array} data
   */
  var initMapData = function(data) {
    for (var i=0; i <data.length; i++) {
      var country = data[i];
      mapData[country.iso2] = country;
    }
  }

  /**
   * Set up the basic elements and projection etc.
   */
  var initMap = function () {
    width = parseInt(container.style("width"), 10);
    height = parseInt(container.style("height"), 10);

    svg = container
      .append("svg")
      .attr("preserveAspectRatio", "xMinYMin meet")
      .attr("viewBox", "0 0 " + width + " " + height);

    var projection = d3
      .geoMercator()
      .translate([width / 2, height / 2])
      .scale(100)
      .center([0, 40]);

    path = d3.geoPath().projection(projection);
  };

  /**
   * Create the tooltip element if it doesn't already exist.
   */
  var initTooltip = function () {
    if (document.getElementsByClassName("js-map-tooltip").length == 0) {
      tooltip = d3
        .select("body")
        .append("div")
        .classed("map-tooltip js-map-tooltip", true);
    } else {
      tooltip = d3.select(".js-map-tooltip");
    }
  };

  /**
   * Listen for clicks on the buttons that hilite certain countries.
   */
  var initListeners = function () {
    var committedBtn = document.querySelector('.js-map-committed');
    committedBtn.addEventListener('click', function(event) {
      hiliteCountries('committed');
      event.preventDefault();
    });

    var implementationBtn = document.querySelector('.js-map-implementation');
    implementationBtn.addEventListener('click', function(event) {
      hiliteCountries('implementation');
      event.preventDefault();
    });
  };

  /**
   * Draw the map using supplied data.
   * @param {object} geojsonData
   */
  var generateMap = function (geojsonData) {
    svg
      .selectAll("path")
      .data(geojsonData.features)
      .enter()
        .append("path")
        .attr("class", function(d) {
          var cls = ' js-map-country';
          if (getCountryProp(d, 'committed_central')) {
            cls += ' js-map-committed-central';
          }
          if (getCountryProp(d, 'committed_public')) {
            cls += ' js-map-committed-public';
          }
          if (getCountryProp(d, 'implementation_central')) {
            cls += ' js-map-implementation-central';
          }
          if (getCountryProp(d, 'implementation_public')) {
            cls += ' js-map-implementation-public';
          }
          return cls;
        })
        .attr("d", path)
          .on("mouseover", onMouseover)
          .on("mousemove", onMousemove)
          .on("mouseout", onMouseout)
          .on("zoom", zoom);

    var zoom = d3
      .zoom()
      .scaleExtent([1, 5])
      .on("zoom", function (event) {
        svg.selectAll("path").attr("transform", event.transform);
      });

    svg.call(zoom);
  };

  /**
   * Cursor has entered a country - show the tooltip.
   * @param {object} event The event.
   * @param {object} d The country object.
   */
  var onMouseover = function (event, d) {
    tooltip.html(tooltipFormat(d));
    tooltip.style("visibility", "visible");
  };

  /**
   * Position the tooltip in relation to cursor.
   * @param {object} event The event.
   * @param {object} d The country object.
   */
  var onMousemove = function (event, d) {
    var tooltipRect = d3
      .select(".js-map-tooltip")
      .node()
      .getBoundingClientRect();
    var tooltipHeight = tooltipRect.height;
    var tooltipWidth = tooltipRect.width;

    // Position above the cursor:
    tooltip
      .style("top", event.pageY - (tooltipHeight + 10) + "px")
      .style("left", event.pageX - tooltipWidth / 2 + "px");
  };

  /**
   * The cursor has left a country - hide the tooltip.
   * @param {object} event The event.
   * @param {object} d The country object.
   */
  var onMouseout = function (event, d) {
    tooltip.style("visibility", "hidden");
  };

  /**
   * Set the content of the tooltip.
   * @param {object} d The country object.
   * @returns string HTML for the tooltip.
   */
  var tooltipFormat = function (d) {
    let text = "<strong>" + getCountryProp(d, "name") + "</strong>";
    text += "<br>Committed central: " + getCountryProp(d, "committed_central");
    text += "<br>Committed public: " + getCountryProp(d, "committed_public");
    text += "<br>Implementation central: " + getCountryProp(d, "implementation_central");
    text += "<br>Implementation public: " + getCountryProp(d, "implementation_public");
    return text;
  };

  /**
   * Get a property about a country from its path element.
   *
   * We use the data that's passed in from the back end, that's now in
   * the mapData object. We need the two-letter ISO value from the d3 element
   * to find the right data in the mapData object.
   *
   * @param {object} d The d3 element that's been clicked, hovered over, etc.
   * @param {string} key The name of a piece of info like 'name', 'url', implementation_central', etc.
   * @returns string
   */
  var getCountryProp = function (d, key) {
    let iso = d.properties.iso_a2;
    if (iso in mapData) {
      if (key in mapData[iso]) {
        return mapData[iso][key];
      } else {
        console.error(
          "No '" + key +"' property found in mapData for ISO '" + iso + "'"
        );
      }
    } else {
      console.error("No iso_a2 value found in " + d.properties);
    }
    return '';
  }

  /**
   * 
   * @param {string} kind Either "committed" or "implementation"
   */
  var hiliteCountries = function(kind) {
    // Turn off any existing hiliting:
    d3.selectAll(".js-map-country.hilite-central").classed("hilite-central", false);
    d3.selectAll(".js-map-country.hilite-public").classed("hilite-public", false);

    // Hilite this kind of country:
    d3.selectAll(".js-map-" + kind + "-central").classed("hilite-central", true);
    d3.selectAll(".js-map-" + kind + "-public").classed("hilite-public", true);
  }

  return publicAPIs;
})();



// Ensure we have everything required before initialising:
if (
  d3 &&
  geojsonPath &&
  mapData &&
  document.querySelectorAll(mapSelector).length
) {
  worldMap.init({
    mapSelector: mapSelector,
    mapData: mapData,
    geojsonPath: geojsonPath,
  });
}
