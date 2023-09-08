/**
 * The global map.
 *
 * This instatiates itself, assuming that the map element is present, along with
 * the variables it requires. See the end of the file, where it checks for their
 * presence before initialising and passing those into worldMap.init().
 *
 * See the Django managment command for how we generate the topoJSON map file.
 *
 * What it expects:
 *
 * topojsonPath - The path to a topoJSON file for generating the map.
 *  Each country should have these properties (others are ignored):
 *    - ISO_A2 - e.g. "DJ"
 *    - NAME - e.g. "Djibouti"
 *
 * mapData - An array of objects, each one about a country, like this:
 *     {
 *       "name": "Djibouti",
 *       "iso2": "DJ",
 *       "url": "/en/map/country/djibouti/",
 *       "lat": "11.6",
 *       "lon": "43.15",
 *       "oo_support": "No engagement",
 *       "category": "planned",
 *     }
 *
 * ooEngagedValues - An array of strings. The values we count as OO being
 *   "engaged" with, as used in the oo_support field in mapData objects.
 *
 * A div with the selector defined in mapSelector, below.
 *
 * Assumes d3.js v5 and topojson.js v3 have been loaded.
 */

// The selector we use to find the element into which we put the map:
const mapSelector = ".js-map";

const worldMap = (function () {
  "use strict";

  var publicAPIs = {};

  // Variables that will be set elsewhere in the code:
  var mapData = {};
  var categories = [];
  var ooEngagedValues = [];
  var container = null;
  var projection = null;
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
   *  topojsonPath: path to topoJSON file to draw the map with.
   */
  publicAPIs.init = function (options) {
    ooEngagedValues = options.ooEngagedValues;

    container = d3.select(options.mapSelector);

    initMapData(options.mapData);
    initMap();
    initTooltip();
    initListeners();

    d3.json(options.topojsonPath).then(function (topojsonData) {
      generateMap(topojsonData);

      // On load we set the initial state by setting all buttons to active:
      setActiveButtons(document.querySelectorAll(".js-map-filter"));
    });
  };

  // PRIVATE METHODS

  /**
   * Take the map data array from the back end and transform it into an object
   * keyed by the iso2 values.
   * Sets the mapData object and categories array.
   * @param {array} data
   */
  var initMapData = function (data) {
    for (var i = 0; i < data.length; i++) {
      var country = data[i];
      mapData[country.iso2] = country;
      if (country.category && categories.includes(country.category) === false) {
        categories.push(country.category);
      }
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
   * Create the tooltip element if it doesn't already exist.
   */
  var initTooltip = function () {
    if (document.getElementsByClassName("js-map-tooltip").length == 0) {
      tooltip = d3
        .select("body")
        .append("div")
        .classed("map__tooltip js-map-tooltip", true);
    } else {
      tooltip = d3.select(".js-map-tooltip");
    }
  };

  /**
   * Listen for clicks on the buttons that hilite certain countries.
   *
   * Each one should have the "js-map-filter" class.
   * And an attribute like:
   *  data-map-hilites="planned"
   *
   * (It should be possible to multiple category values, like
   *   data-map-hilites="planned|implementing"
   * but we don't currently use that ability).
   */
  var initListeners = function () {
    document.addEventListener("click", function (event) {
      // Is it a click on one of the buttons:
      if (event.target.matches('.js-map-filter')) {
        setActiveButtons([event.target]);
        event.preventDefault();
      }
    });

    // Just clicking on the background removes any existing hiliting.
    svg.on("click", function(event, d) {
      setActiveButtons();
    });
  };

  /**
   * Set which button is now active, and change map hilites accordingly.
   * @param {array} btnEls The elements which should be active. Or null if none of them should be.
   */
  var setActiveButtons = function (btnEls) {
    document.querySelectorAll(".js-map-filter").forEach(function(el) {
      el.classList.remove("--active");
    });

    // We'll hilite countries with these categories:
    var catsToHilite = [];

    if (btnEls) {
      btnEls.forEach(function(el) {
        el.classList.add("--active");

        var cats = el.getAttribute("data-map-hilites").split("|");
        cats.forEach(function(cat) {
          if ( ! catsToHilite.includes(cat)) {
            catsToHilite.push(cat);
          }
        })
      });
    }
    hiliteCountries(catsToHilite);
  }

  /**
   * Draw the map using supplied data.
   * @param {object} topojsonData
   */
  var generateMap = function (topojsonData) {
    ///////////////////////////////////////////////////////
    // ADD COUNTRIES

    // The ne_50m_admin_0_countries key is set in the data we originally
    // download from Natural Earth. It will change if we download different
    // data, e.g. a different resolution.
    const countries = topojson.feature(
      topojsonData,
      topojsonData.objects.countries,
    );

    svg
      .selectAll("path")
      .data(countries.features)
      .enter()
        .append("path")
        .attr("class", function(d) {
          var cls = ' js-map-country';
          var cat = getCountryProp(d, 'category');
          if (cat) {
            cls += ' js-map-'+cat;
          }

        // if (ooEngagedValues.indexOf(getCountryProp(d, 'oo_support')) > -1) {
        //   cls += ' map-engaged';
        // }

        return cls;
      })
      .attr("d", path)
      .on("click", onClick)
      .on("mouseover", onMouseover)
      .on("mousemove", onMousemove)
      .on("mouseout", onMouseout)
      .on("zoom", zoom);

    ///////////////////////////////////////////////////////
    // ADD CIRCLES

    // Get the lat/lon of every country that has them, to show a circle in each
    // country where OO has a presence.
    var circles = [];

    for (var iso in mapData) {
      if (mapData[iso].lon) {
        if (ooEngagedValues.indexOf(mapData[iso].oo_support) > -1) {
          circles.push(
            projection([
              parseFloat(mapData[iso].lon),
              parseFloat(mapData[iso].lat),
            ])
          );
        }
      }
    }

    svg
      .selectAll("circle")
      .data(circles)
      .enter()
      .append("circle")
      .attr("class", "map__circle")
      .attr("cx", function (d) {
        return d[0];
      })
      .attr("cy", function (d) {
        return d[1];
      })
      .attr("r", "3px");

    ///////////////////////////////////////////////////////
    // ENABLE ZOOM

    var zoom = d3
      .zoom()
      .scaleExtent([1, 5])
      .on("zoom", function (event) {
        svg.selectAll("path").attr("transform", d3.event.transform);
        svg.selectAll("circle").attr("transform", d3.event.transform);
      });

    svg.call(zoom);

    function onZoomClick(zoomLevel) {
      svg.transition().delay(50).duration(300).call(zoom.scaleBy, zoomLevel);
    }

    d3.selectAll(".js-map-zoomin").on("click", function () {
      onZoomClick(1.5);
    });
    d3.selectAll(".js-map-zoomout").on("click", function () {
      onZoomClick(0.5);
    });
  };

  /**
   * When a country has been clicked, this is called.
   * @param {object} event The event.
   * @param {object} d The country object.
   */
  var onClick = function (d, i) {
    var url = getCountryProp(d, "url");
    if (url) {
      window.location = url;
    }
  };

  /**
   * Cursor has entered a country - show the tooltip.
   * @param {object} event The event.
   * @param {object} d The country object.
   */
  var onMouseover = function (d, i) {
    let html = tooltipFormat(d);
    if (html) {
      tooltip.html(html);
      tooltip.style("visibility", "visible");
    }
  };

  /**
   * Position the tooltip in relation to cursor.
   * @param {object} event The event.
   * @param {object} d The country object.
   */
  var onMousemove = function (d, i) {
    var tooltipRect = d3
      .select(".js-map-tooltip")
      .node()
      .getBoundingClientRect();
    var tooltipHeight = tooltipRect.height;
    var tooltipWidth = tooltipRect.width;

    // Position above the cursor:
    tooltip
      .style("top", event.pageY - (tooltipHeight + 7) + "px")
      .style("left", event.pageX - tooltipWidth / 2 + "px");
  };

  /**
   * The cursor has left a country - hide the tooltip.
   * @param {object} event The event.
   * @param {object} d The country object.
   */
  var onMouseout = function (d, i) {
    tooltip.style("visibility", "hidden");
  };

    /**
     * Set the content of the tooltip.
     * @param {object} d The country object.
     * @returns string HTML for the tooltip.
     */
    var tooltipFormat = function (d) {
      let name = getCountryProp(d, "name");
      let html = '';
      if (name) {
        html = "<strong>" + getCountryProp(d, "name") + "</strong>";
      }
      // text += "<br>Category: " + getCountryProp(d, "category");
      return html;
    };

  /**
   * Get a property about a country from its path element.
   *
   * We use the data that's passed in from the back end, that's now in
   * the mapData object. We need the two-letter ISO value from the d3 element
   * to find the right data in the mapData object.
   *
   * @param {object} d The d3 element that's been clicked, hovered over, etc.
   * @param {string} key The name of a piece of info like 'name', 'url', 'category', etc.
   * @returns string
   */
  var getCountryProp = function (d, key) {
    let iso = d.properties.ISO_A2;
    if (iso in mapData) {
      if (key in mapData[iso]) {
        return mapData[iso][key];
      } else {
        console.error(
          "No '" + key + "' property found in mapData for ISO '" + iso + "'"
        );
      }
    } else {
      console.error(
        "No iso_a2 value found for " +
          d.properties.NAME +
          " (" +
          iso +
          ") when looking for " +
          key
      );
    }
    return "";
  };

  /**
   * Add classes to countries based on their category.
   *
   * @param {array} hiliteCats An array of strings like
   *  ["planned", "implementing"]
   *  If it's an empty array then all hilite classes will be removed.
   */
  var hiliteCountries = function(hiliteCats) {
    // Turn off any existing hiliting:
    var unHiliteCats = categories.filter(function(c) {
      return hiliteCats.indexOf(c) < 0;
    });
    unHiliteCats.forEach(function(cat) {
      d3.selectAll(".js-map-country.map__hilite-"+cat).classed("map__hilite-"+cat, false);
    });

    // Hilite this kind of country:
    hiliteCats.forEach(function(cat) {
      var clss = "map__hilite-"+categories[0];
      if (categories.includes(cat)) {
        clss = "map__hilite-"+cat;
      }
      d3.selectAll(".js-map-"+cat).classed(clss, true);
    });
  }

  return publicAPIs;
})();

// Ensure we have everything required before initialising:
if (
  typeof d3 !== "undefined" &&
  typeof topojsonPath !== "undefined" &&
  typeof mapData !== "undefined" &&
  typeof ooEngagedValues !== "undefined" &&
  document.querySelectorAll(mapSelector).length
) {
  worldMap.init({
    mapSelector: mapSelector,
    mapData: mapData,
    topojsonPath: topojsonPath,
    ooEngagedValues: ooEngagedValues,
  });
}
