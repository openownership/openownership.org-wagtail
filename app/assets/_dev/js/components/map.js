/**
 * The global map.
 *
 * This instatiates itself, assuming that the map element is present, along with
 * the variables it requires. See the end of the file, where it checks for their
 * presence before initialising and passing those into worldMap.init().
 *
 * What it expects:
 *
 * geojsonPath - The path to a geojson file for generating the map.
 *
 * mapData - An array of objects, each one about a country, like this:
 *     {
 *       "name": "Djibouti",
 *       "iso2": "DJ",
 *       "url": "/en/map/country/djibouti/",
 *       "lat": "11.6",
 *       "lon": "43.15",
 *       "oo_support": "No engagement",
 *       "committed_central": true,
 *       "committed_public": true,
 *       "implementation_central": false,
 *       "implementation_public": false
 *     }
 *
 * ooEngagedValues - An array of strings. The values we count as OO being
 *   "engaged" with, as used in the oo_support field in mapData objects.
 *
 * A div with the selector defined in mapSelector, below.
 *
 * Assumes d3.js version 7 has been loaded.
 */


// The selector we use to find the element into which we put the map:
const mapSelector = ".js-map";

const worldMap = (function () {
  "use strict";

  var publicAPIs = {};

  // Variables that will be set elsewhere inthe code:
  var mapData = {};
  var ooEngagedValues = [];
  var container = null;
  var projection = null;
  var svg = null;
  var width = null;
  var height = null;
  var path = null;

  /**
   * Call this to initialise everything.
   * @param {object} options Should have:
   *  mapSelector: string, the selector of the element into which we put the map
   *  mapData: array of objects, one per country with OO data.
   *  geojsonPath: path to geojson file to draw the map with.
   */
  publicAPIs.init = function (options) {

    ooEngagedValues = options.ooEngagedValues;

    container = d3.select(options.mapSelector);

    initMapData(options.mapData);
    initMap();
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
    mapData = data;
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

    projection = d3
      .geoMercator()
      .translate([width / 2, height / 2])
      .scale(100)
      .center([0, 40]);

    path = d3.geoPath().projection(projection);
  };

  /**
   * Listen for clicks on the buttons that hilite certain countries.
   */
  var initListeners = function () {
    var committedBtn = document.querySelector('.js-map-committed');
    committedBtn.addEventListener('click', function(event) {
      hiliteCountries(['committed-central', 'committed-public']);
      event.preventDefault();
    });

    var committedCentralBtn = document.querySelector('.js-map-committed-central');
    committedCentralBtn.addEventListener('click', function(event) {
      hiliteCountries(['committed-central']);
      event.preventDefault();
    });

    var committedPublicBtn = document.querySelector('.js-map-committed-public');
    committedPublicBtn.addEventListener('click', function(event) {
      hiliteCountries(['committed-public']);
      event.preventDefault();
    });

    var implementationBtn = document.querySelector('.js-map-implementation');
    implementationBtn.addEventListener('click', function(event) {
      hiliteCountries(['implementation-central', 'implementation-public']);
      event.preventDefault();
    });

    var implementationCentralBtn = document.querySelector('.js-map-implementation-central');
    implementationCentralBtn.addEventListener('click', function(event) {
      hiliteCountries(['implementation-central']);
      event.preventDefault();
    });

    var implementationPublicBtn = document.querySelector('.js-map-implementation-public');
    implementationPublicBtn.addEventListener('click', function(event) {
      hiliteCountries(['implementation-public']);
      event.preventDefault();
    });

    // Just clicking on the background removes any existing hiliting.
    svg.on("click", function(event, d) {
      hiliteCountries([]);
    });
  };

  /**
   * Draw the map using supplied data.
   * @param {object} geojsonData
   */
  var generateMap = function (geojsonData) {

    ///////////////////////////////////////////////////////
    // ADD COUNTRIES

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

          // if (ooEngagedValues.indexOf(getCountryProp(d, 'oo_support')) > -1) {
          //   cls += ' map-engaged';
          // }

          return cls;
        })
        .attr("d", path)
          .on("click", onClick)
          .on("zoom", zoom);

    ///////////////////////////////////////////////////////
    // ADD CIRCLES

    // Get the lat/lon of every country that has them, to show a circle in each
    // country where OO has a presence.
    var circles = [];

    for (var iso in mapData) {
      if (mapData[iso].lon) {
        if (ooEngagedValues.indexOf(mapData[iso].oo_support) > -1) {
          circles.push(projection([
            parseFloat(mapData[iso].lon),
            parseFloat(mapData[iso].lat)
          ]))
        }
      }
    }

    svg
      .selectAll("circle")
      .data(circles)
      .enter()
      .append("circle")
      .attr("class", "map__circle")
      .attr("cx", function (d) { return d[0]; })
      .attr("cy", function (d) { return d[1]; })
      .attr("r", "3px");

    ///////////////////////////////////////////////////////
    // ENABLE ZOOM

    var zoom = d3
      .zoom()
      .scaleExtent([1, 5])
      .on("zoom", function (event) {
        svg.selectAll("path").attr("transform", event.transform);
        svg.selectAll("circle").attr("transform", event.transform);
      });

    svg.call(zoom);

    function onZoomClick(zoomLevel) {
      svg.transition()
        .delay(50)
        .duration(300)
        .call(zoom.scaleBy, zoomLevel);
    }

    d3.selectAll('.js-map-zoomin').on('click', function() {
      onZoomClick(1.5);
    });
    d3.selectAll('.js-map-zoomout').on('click', function() {
      onZoomClick(0.5);
    });
  };

  /**
   * When a country has been clicked, this is called.
   * @param {object} event The event.
   * @param {object} d The country object.
   */
  var onClick = function (event, d) {
    var url = getCountryProp(d, "url");
    if (url) {
      window.location = url;
    }
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
      console.error(
        "No iso_a2 value found for " + d.properties.name + " when looking for " + key
      );
    }
    return '';
  }

  /**
   * Add classes to countries based on whether they've committed/implemented.
   *
   * @param {array} kinds An array of strings like
   *  ["committed-central", "committed-public"]
   *  If it's an empty array then all hilite classes will be removed.
   */
  var hiliteCountries = function(kinds) {
    // Turn off any existing hiliting:
    d3.selectAll(".js-map-country.map__hilite-central").classed("map__hilite-central", false);
    d3.selectAll(".js-map-country.map__hilite-public").classed("map__hilite-public", false);

    // Hilite this kind of country:
    for (var i=0; i<kinds.length; i++) {
      var clss = "map__hilite-central";
      if (kinds[i].endsWith("public")) {
        clss = "map__hilite-public";
      }
      d3.selectAll(".js-map-" + kinds[i]).classed(clss, true);
    }
  }

  return publicAPIs;
})();



// Ensure we have everything required before initialising:
if (
  typeof d3 !== 'undefined' &&
  typeof geojsonPath !== 'undefined' &&
  typeof mapData !== 'undefined' &&
  typeof ooEngagedValues !== 'undefined' &&
  document.querySelectorAll(mapSelector).length
) {
  worldMap.init({
    mapSelector: mapSelector,
    mapData: mapData,
    geojsonPath: geojsonPath,
    ooEngagedValues: ooEngagedValues
  });
}
