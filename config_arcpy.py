import arcpy 
arcpy.env.overwriteOutput=True
arcpy.env.workspace="gis/main_map/main_map.gdb"


# gis layers
# statring_path='C:/thesis/gis/scripts/thesis_code/external_files/gis_layers/'
occupation='external_files/gis_layers/governmental_layers.gdb/occupation'
jlm_boundry='external_files/gis_layers/governmental_layers.gdb/jlm_city_boundries'
jlm_metro='external_files/gis_layers/governmental_layers.gdb/jlm_metro'
statisticalareas_2022='external_files/gis_layers/governmental_layers.gdb/statisticalareas_demography2022'
jlm_city_boundries='external_files/gis_layers/governmental_layers.gdb/jlm_city_boundries'
settlements='external_files/gis_layers/settlements/settlements.shp'
original_bus_layer='external_files/gis_layers/gtfs_layers.gdb/bus_routes_from_GTFS' # bus routes layer
stops_from_GTFS='external_files/gis_layers/gtfs_layers.gdb/stops_from_GTFS'




# GIS_links={'statisticalareas_2022':'external_files/gis_layers/governmental_layers.gdb/statisticalareas_demography2022',
# 'jlm_metropolitan_boundries':'external_files/gis_layers/governmental_layers.gdb/jlm_metro',
# 'jlm_city_boundries':'external_files/gis_layers/governmental_layers.gdb/jlm_city_boundries',
# 'settlements':'external_files/gis_layers/settlements/settlements.shp',
# 'bus_routes_from_GTFS':'external_files/gis_layers/gtfs_layers.gdb/bus_routes_from_GTFS',
# 'stops_from_GTFS':'external_files/gis_layers/gtfs_layers.gdb/stops_from_GTFS'}

# gis fields and layers names
copy_bus_layer='copy_buses'
JLM_buses_clip='bus_routes_calculate'
jlm_city_boundries='external_files/gis_layers/governmental_layers.gdb/jlm_city_boundries'
final_bus_layer='bus_routes_jlm_metro' # jerusalem bus lines layer name
inside_jlm_field='jlm_route_length_km' # field indicates percent of line inside jlm
whole_route_field='whole_route_length_km' # field indicates whole length of route
percent_inside_jlm_field='percent_inside_jlm' # final percent of line in jlm
threshold_value=0.25 # threshold percent to determine line as relevant to tehe research
stops_jlm_layer_name='stopsend'



