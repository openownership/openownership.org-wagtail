import json
from pathlib import Path

from consoler import console
from django.core.management.base import BaseCommand


# Where we save the output to, overwriting whatever's already there.
OUT_FILE = Path(Path.cwd() / 'assets' / 'dist' / 'data' / 'worldmap_topo.json')


class Command(BaseCommand):
    """
    For processing a topoJSON file of a world map to a format we use for /en/map/.

    How to make the input file:

    1. From https://www.naturalearthdata.com/downloads/50m-cultural-vectors/
       click the "Download countries" link to get `ne_50m_admin_0_countries.zip`

    2. Drag the zipped file on to https://mapshaper.org and import all the files.

    3. Click "Simplify" and "Apply".

    4. Drag Settings slider to 10% (or whatever works for you).

    5. Click "Repair" (top left).

    6. Click "Export".

    7. Change "Layer name" to "countries". Select "TopoJSON". Click "Export" button.

    8. Use that file as input for this script which will save a smaller, tweaked
       version to the correct location, overwriting the existing one.

    NOTE: If you move these instructions, also change the pointer to them
    from assets/_dev/js/components/map.js and templates/content/map_page.jinja

    """
    help = (
        "Converts the specified file to work with our map, and replaces "
        "the map's existing TopoJSON file."
    )

    def add_arguments(self, parser):
        parser.add_argument("-f", "--file", required=True, type=str)

    def handle(self, **options):
        in_file = Path(options["file"])
        if not Path.is_file(in_file):
            console.error("No input file found at %s" % in_file)
            exit(1)

        console.info("Converting %s" % in_file)

        with open(in_file) as f:
            topodata = json.load(f)

        new_geometries = []

        for geom in topodata["objects"]["countries"]["geometries"]:
            # A few have -99 as their ISO A2 value but have an ISO A2 EH
            # which we'll use instead so that we have something.
            # See https://github.com/nvkelso/natural-earth-vector/issues/284
            if geom["properties"]["ISO_A2"] == "-99":
                iso_a2 = geom["properties"]["ISO_A2_EH"]
            else:
                iso_a2 = geom["properties"]["ISO_A2"]

            new_geometries.append({
                "arcs": geom["arcs"],
                "type": geom["type"],
                "properties": {
                    "ISO_A2": iso_a2,
                    "NAME": geom["properties"]["NAME"],
                },
            })

        topodata["objects"]["countries"]["geometries"] = new_geometries

        with open(OUT_FILE, "w", encoding="utf-8") as f:
            json.dump(topodata, f, indent=None, separators=(',', ':'))

        console.success("Converted and saved to %s" % OUT_FILE)
