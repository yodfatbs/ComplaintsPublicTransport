import pandas as pd
import numpy as np
import osmnx as ox
ox.settings.log_console = True
ox.settings.max_query_area_size = 25e12
import geopandas as gpd
from shapely.geometry import Point


def find_start_end_per_line():

    """ 
    function returns:dataframe of lines with data of 1st and last stops 
    """

    stop_route=pd.read_csv('outputs/direcness_measurement.csv')
        
        #  take only stops in JLM metro area, 1st and last stops for each route
    gdf_pois_jlm = gpd.GeoDataFrame(stop_route, 
                                    geometry=[Point(lon, lat) for lat, lon in zip(stop_route['stop_lat'], stop_route['stop_lon'])])

    min_idx = gdf_pois_jlm.groupby('route_desc')['StationOrder'].idxmin() # find 1st stop in each route

    max_idx = gdf_pois_jlm.groupby('route_desc')['StationOrder'].idxmax() # find last stop in each route

    result_idx = pd.concat([min_idx, max_idx]).sort_values() #create dataframe with geographic data of 1st and last stops for each route
    start_end=gdf_pois_jlm.loc[result_idx]
    start_end['StationOrder'] = np.where(start_end['StationOrder'] ==1, 'startcode', 'endcode')
    start_end['shape_dist_traveled'] = np.where(start_end['StationOrder']=='startcode', 0, start_end['trip_km_fact'].astype(float)*1000)

    return start_end

###########################################################################################
###########################################################################################
def find_shortest_route(start_end_stops_df):

    """ 
    function makes: find shortest driving distance between 1st and last stop for each busline
    function gets:  dataframe with 1st and last stops coordinates for each line, coordinates for JLM area
    function returns:dataframe with bus lines and shortest distnance between 1st and last stop (in meters)
    """
    north, south, east, west = 32.14, 31.48, 35.41, 34.94  # coordinates of JLM metro area

    # create driving networx of JLM metropolitan area
    il_roads = ox.graph_from_bbox(north, south, east, west, network_type='drive')
    pois=start_end_stops_df.groupby(['route_desc'])['geometry'].apply(list).reset_index(name='geometry')

#2.calculate distance between 1st and last stop for each bus line
    route_desc=[]
    direct_length=[]
    for i in range(len(pois)):
        print(i)
        route_desc.append(pois['route_desc'][i])
        origin = ox.nearest_nodes(il_roads, pois['geometry'][i][0].x, pois['geometry'][i][0].y)
        destination = ox.nearest_nodes(il_roads, pois['geometry'][i][1].x, pois['geometry'][i][1].y)
        route=ox.shortest_path(il_roads, origin,destination)
        if not isinstance (route, list):
            route=[-1]
            direct_length.append(route)
            print('problem')
        else:
            direct_length.append(round(
                sum(ox.utils_graph.get_route_edge_attributes(il_roads, route, 'length')),2)) # get the length of every edge on route)
#3. create data frame of the distances
    direct_distance = pd.DataFrame()
    direct_distance['route_desc']=route_desc
    direct_distance['direct_length'] = direct_length
    return direct_distance  

###########################################################################################
###########################################################################################
def calaulate_directness_level(start_end, car_length):
    endcode=start_end[start_end['StationOrder']=='endcode']
    merged=pd.merge(car_length,endcode[['route_desc', 'trip_km_fact']], on='route_desc', how='inner')
    merged['direct_length_km']=round(merged['direct_length']/1000, 3)
    merged['directness']=round(merged['direct_length_km']/merged['trip_km_fact'], 2)
    merged['directness']=np.where(merged['directness']>1,1,merged['directness'])
    return merged  
###########################################################################################
###########################################################################################

def create_directness_measurement():
    by_bus=find_start_end_per_line()
    by_car=find_shortest_route(by_bus)
    final_directness=calaulate_directness_level(by_bus, by_car)
    final_directness.to_csv('outputs/final_directness.csv')