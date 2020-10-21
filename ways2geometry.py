import pandas as pd
import geopandas as gpd
import contextily as ctx  # Package to retrieve OSM and Stamen tile maps. Supports EPSG:4326 and EPSG:3857
from shapely.ops import transform
from shapely.geometry import LineString
from ast import literal_eval

def ways2geometry(overpass_result_object):
    """Takes an OverpassResult object as returned by the OSMPythonTools query function.\n
    Converts OverpassResult result object into a Pandas Geodataframe with initialised geometry attribute. Also returns dict with OSM tags for each way.\n
    Currently only supports queries for OSM ways (e.g. elementType=['way'])."""
    tunnel_json = overpass_result_object.toJSON()
    # Read ['elements'] attribute into a df:
    df = pd.DataFrame.from_records(tunnel_json['elements'])
    df.rename(columns={'nodes': 'node_IDs'}, inplace=True)
    # Clean up the geometry column which contains the coordinates, but has 'lat', 'lon' strings etc.
    df['geometry'] = df['geometry'].astype(str)
    df['geometry'].replace({r"{'lat': ": r'(',
                            r"'lon': ": '',
                            r'}': r')'}, inplace=True, regex=True)
    # Convert string representations into a list of tuples of floats.
    df['geometry'] = [literal_eval(row) for row in df['geometry']]
    if not isinstance(df.geometry[1][1], tuple):
        raise ValueError("Geometry coordinates must be of <class 'tuple'>. Conversion failed.")


    # Unpack the 'tags' into a dictionary. This way we avoid NaNs and just have unique dict for every way ID key.
    way_tags = {}
    for way in df[['id', 'tags']].itertuples():
        way_tags[way.id] = way.tags
    # Finally delete the 'tags' col (no longer needed). axis=1 specifies column, not row.
    df.drop(columns='tags', axis=1, inplace=True)

    # Construct a Geopandas gdf and enable the 'geometry' column.
    gdf = gpd.GeoDataFrame(df, geometry=df['geometry'].apply(lambda row: LineString(row)), crs='epsg:4326')  # EPSG: 4326 is WGS84 (Lat and Long)
    # Flip the LineString coords as they are the wrong way around.
    gdf['geometry'] = gdf.geometry.map(lambda linestring: transform(lambda x, y: (y, x), linestring))
    gdf.set_crs(epsg='4326', inplace=True)  # Set lon lat system again.

    return gdf, way_tags

def preview_ways(geodataframe):
    """Plots a preview map (similar to Overpass Turbo) showing location of all the ways found through the Overpass query.\n
    Similar to Overpass Turbo."""

    # Map tiles from contextily are provided in the Web Mercator coordinate reference system (EPSG:3857).
    gdf_wm = geodataframe.to_crs(epsg='3857')
    # Add a column for the centre of each geometry
    gdf_wm['centroid'] = gdf_wm.geometry.centroid
    # Create plot using matplotlib functionality
    ax = gdf_wm.plot(figsize=(10, 6), color='blue', linewidth=2)
    gdf_wm.centroid.plot(ax=ax, marker='o', color='red', alpha=0.5, markersize=40)
    # Add a basemap from contextily. This map should look a lot like Overpass Turbo!
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
