from typing import List, Optional

import folium
import geopandas as gpd
import numpy as np #TODO np is not accessed
import pandas as pd
from shapely.geometry import Point

from yamm.constructs.match import Match
from yamm.constructs.trace import Trace #TODO Trace is not used?
from yamm.maps.map_interface import MapInterface
from yamm.utils.crs import XY_CRS, LATLON_CRS
import matplotlib.pyplot as plt


def plot_geofence(geofence, m=None):
    """_summary_

    Args:
        geofence (_type_): _description_
        m (_type_, optional): _description_. Defaults to None.

    Raises:
        NotImplementedError: _description_

    Returns:
        _type_: _description_
    """
    if not geofence.crs == LATLON_CRS:
        raise NotImplementedError("can currently only plot a geofence with lat lon crs")

    if not m:
        c = geofence.geometry.centroid.coords[0]
        m = folium.Map(location=[c[1], c[0]], zoom_start=11)

    folium.GeoJson(geofence.geometry).add_to(m)

    return m


def plot_trace(trace, m=None, point_color="yellow", line_color="green"):
    """
    plot trace takes in trace, m, point_color and the color of the line.

    Args:
        trace (_type_): _description_
        m (_type_, optional): _description_. Defaults to None.
        point_color (str, optional): _description_. Defaults to "yellow".
        line_color (str, optional): _description_. Defaults to "green".

    Returns:
        _type_: _description_
    """

    if not trace.crs == LATLON_CRS:
        trace = trace.to_crs(LATLON_CRS)

    if not m:
        mid_coord = trace.coords[int(len(trace) / 2)]
        m = folium.Map(location=[mid_coord.y, mid_coord.x], zoom_start=11)

    for i, c in enumerate(trace.coords):
        folium.Circle(
            location=(c.y, c.x), radius=5, color=point_color, tooltip=i
        ).add_to(m)

    folium.PolyLine([(p.y, p.x) for p in trace.coords], color=line_color).add_to(m)

    return m


def plot_matches(matches: List[Match], road_map: MapInterface):
    """
    plots a trace and the relevant matches on a folium map

    :param matches: the matches
    :param road_map: the road map

    :return: the folium map
    """

    def match_to_road(m):
        """
        match_to_road ...

        Args:
            m (_type_): _description_

        Returns:
            _type_: _description_
        """
        d = {"road_id": m.road.road_id}

        metadata = m.road.metadata
        u = metadata["u"]
        v = metadata["v"]

        edge_data = road_map.g.get_edge_data(u, v)

        road_key = list(edge_data.keys())[0]

        # TODO: this should be generic over all road maps
        geom_key = road_map._geom_key

        road_geom = edge_data[road_key][geom_key]

        d["geom"] = road_geom

        return d

    def match_to_coord(m):
        """
        matching to coordinates...

        Args:
            m (_type_): _description_

        Returns:
            _type_: _description_
        """
        d = {
            "road_id": m.road.road_id,
            "geom": Point(m.coordinate.x, m.coordinate.y),
            "distance": m.distance,
        }

        return d
    

    road_df = pd.DataFrame([match_to_road(m) for m in matches if m.road])
    road_df = road_df.loc[road_df.road_id.shift() != road_df.road_id]
    road_gdf = gpd.GeoDataFrame(road_df, geometry=road_df.geom, crs=XY_CRS).drop(
        columns=["geom"]
    )
    road_gdf = road_gdf.to_crs(LATLON_CRS)

    coord_df = pd.DataFrame([match_to_coord(m) for m in matches if m.road])

    coord_gdf = gpd.GeoDataFrame(coord_df, geometry=coord_df.geom, crs=XY_CRS).drop(
        columns=["geom"]
    )
    coord_gdf = coord_gdf.to_crs(LATLON_CRS) # convert coordinates to latlon_crs format.

    mid_i = int(len(coord_gdf) / 2)
    mid_coord = coord_gdf.iloc[mid_i].geometry

    # create a plot of the accuracy of predicted points based on actual map data.
    plot_match_score(coord_gdf,coord_df,road_gdf)

    # create a fmap with folium given the location coordinates
    fmap = folium.Map(location=[mid_coord.y, mid_coord.x], zoom_start=11)

    for coord in coord_gdf.itertuples():
        folium.CircleMarker(
            location=(coord.geometry.y, coord.geometry.x),
            radius=5,
            tooltip=f"road_id: {coord.road_id}\ndistance: {coord.distance}", 
            fill_opacity=1
        ).add_to(fmap)

    for road in road_gdf.itertuples():
        folium.PolyLine(
            [(lat, lon) for lon, lat in road.geometry.coords],
            color="red",
            tooltip=road.road_id,
        ).add_to(fmap)

    return fmap


def plot_map(tmap: MapInterface, m=None):
    """
    summary goes here

    Args:
        tmap (MapInterface): _description_
        m (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    # TODO make this generic to all map types, not just NxMap
    roads = list(tmap.g.edges(data=True))
    road_df = pd.DataFrame([r[2] for r in roads])
    gdf = gpd.GeoDataFrame(road_df, geometry=road_df[tmap._geom_key], crs=tmap.crs)
    if gdf.crs != LATLON_CRS:
        gdf = gdf.to_crs(LATLON_CRS)

    if not m:
        c = gdf.iloc[int(len(gdf) / 2)].geometry.centroid.coords[0]
        m = folium.Map(location=[c[1], c[0]], zoom_start=11)

    for t in gdf.itertuples():
        folium.PolyLine(
            [(lat, lon) for lon, lat in t.geometry.coords], color="red"
        ).add_to(m)

    return m


def plot_match_score(coord_gdf,coord_df,road_gdf):



    y = coord_df.distance # the distances from the expected line. Deviance. 
    x = [x for x in range(0,len(y))] # create blanks for x axis
    #y = np.exp(np.sin(x))

    for coord in coord_gdf.itertuples():
        x_coord = coord.geometry.x
        y_coord = coord.geometry.y
        
    for road in road_gdf.itertuples():
        full_line = [(lat, lon) for lon, lat in road.geometry.coords]

    plt.figure(figsize=(15, 7))
    plt.autoscale(enable=True)
    #plt.stem(x, y)
    plt.scatter(x,y)
    plt.title('Distance To Nearest Road')
    plt.ylabel('Meters')
    plt.xlabel('Point Along The Path')
    plt.show()

