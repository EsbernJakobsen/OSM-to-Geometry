## `OverpassResult` Object Parser and Previewer (for OSM-Python-Tools)
This is to be used in conjunction with the [OSM-Python-Tools](https://github.com/mocnik-science/osm-python-tools) Overpass API query function.

#### What it does
The first function parses the `OverpassResult` object into a geometry-initialised GeoDataframe, and converts the 'ways' coordinates to shapely objects.
It returns a GeoDataframe, and a dictionary with the OSM 'tags'.

The second function plots a quick map of the locations of all the OSM features returned by the query.


#### Prerequisites
The dependencies for this script are:
- Python 3.6>
- Pandas, Geopandas, Shapely
- Contextily

#### To-do
- Add support for OSM nodes and relations

#### Licensing
This software is under the MIT license.