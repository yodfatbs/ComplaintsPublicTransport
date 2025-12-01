import requests
import zipfile
import io
import os
import arcpy

def read_GIS_layers(url, extract_folder, gdb_path):
    # Download the file
    r = requests.get(url)
    r.raise_for_status()

    # Load into memory and extract
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        z.extractall(extract_folder)  # Extract to local folder
    gdb_path = os.path.join(extract_folder, gdb_path)

    return gdb_path

# url = "https://zenodo.org/record/17778363/files/main_map.zip?download=1"
# workspace=read_GIS_layers(url, 'main_map', 'main_map.gdb')
workspace="main_map/main_map/main_map.gdb"

arcpy.env.workspace=workspace

# GIS={
#   "gis_layers": {
#     "occupation": "external_files/gis_layers/governmental_layers.gdb/occupation",
#     "jlm_boundry": "external_files/gis_layers/governmental_layers.gdb/jlm_boundry",
#     "jlm_metro": "external_files/gis_layers/governmental_layers.gdb/jlm_metro",
#     "statisticalareas_2022": "external_files/gis_layers/governmental_layers.gdb/sa_2022",
#     "jlm_city_boundries": "external_files/gis_layers/governmental_layers.gdb/jlm_boundry",
#     "settlements": "external_files/gis_layers/settlements/settlements.shp",
#     "original_bus_layer": "external_files/gis_layers/governmental_layers.gdb/bus_routes",
#     "stops_from_GTFS": "external_files/gis_layers/governmental_layers.gdb/stops" 
#   },
#   "gis_fields_and_names": {
#     "copy_bus_layer": "copy_buses",
#     "JLM_buses_clip": "bus_routes_calculate",
#     "jlm_city_boundries": "external_files/gis_layers/governmental_layers.gdb/jlm_boundry",
#     "final_bus_layer": "bus_routes_jlm_metro",
#     "inside_jlm_field": "jlm_route_length_km",
#     "whole_route_field": "whole_route_length_km",
#     "percent_inside_jlm_field": "percent_inside_jlm",
#     "threshold_value": 0.25,
#     "stops_jlm_layer_name": "stopsend",
#     'bus_routes_inside_jlm':'clipped_bus_routes_inside_jlm',
#     'stop_in_jlm_metro':'jlm_stops'
#   }
# }
governmental_layers_url = "https://zenodo.org/record/17778363/files/governmental_layers.gdb.zip?download=1"
governmental_layers_path = read_GIS_layers(governmental_layers_url, 'governmental_layers', 'governmental_layers.gdb')

settlements_url = "https://zenodo.org/record/17778363/files/settlements.zip?download=1"
settlements_path = read_GIS_layers(settlements_url, 'settlements', 'settlements')

GIS={
  "gis_layers": {
    "occupation": f"{governmental_layers_path}/occupation",
    "jlm_boundry": f"{governmental_layers_path}/jlm_boundry",
    "jlm_metro": f"{governmental_layers_path}/jlm_metro",
    "statisticalareas_2022": f"{governmental_layers_path}/sa_2022",
    "jlm_city_boundries": f"{governmental_layers_path}/jlm_boundry",
    "settlements": "external_files/gis_layers/settlements/settlements.shp",
    "original_bus_layer": f"{governmental_layers_path}/bus_routes",
    "stops_from_GTFS": f"{governmental_layers_path}/stops" 
  },
  "gis_fields_and_names": {
    "copy_bus_layer": "copy_buses",
    "JLM_buses_clip": "bus_routes_calculate",
    "jlm_city_boundries": f"{governmental_layers_path}/jlm_boundry",
    "final_bus_layer": "bus_routes_jlm_metro",
    "inside_jlm_field": "jlm_route_length_km",
    "whole_route_field": "whole_route_length_km",
    "percent_inside_jlm_field": "percent_inside_jlm",
    "threshold_value": 0.25,
    "stops_jlm_layer_name": "stopsend",
    'bus_routes_inside_jlm':'clipped_bus_routes_inside_jlm',
    'stop_in_jlm_metro':'jlm_stops'
  }
}

Links={
  "cbs_links": {
    "demographic_urb_path": "https://zenodo.org/record/17778363/files/socio_eco_urb.xlsx?download=1",
    "demographic_reg_path": "https://zenodo.org/record/17778363/files/socio_eco_regional.xlsx?download=1",
    "demographic_sub_path": "https://zenodo.org/record/17778363/files/socio_eco_suburb.xlsx?download=1",
    "ultraorthodox_path": "https://zenodo.org/record/17778363/files/ultraorthodox_state.xlsx?download=1"
  },
  "buses_links": {
    "rishui_lines": "https://zenodo.org/record/17778363/files/rishui_lines.xlsx?download=1",
    "NPTA_extractions": "https://zenodo.org/record/17778363/files/extract_npta_060324.xlsx?download=1",
    "comlaints": "external_files/transportation_ministry/public complaints jan22-jun 23.xlsx" #this file is restricted, due to personal data
  },
  "GTFS_links": {
    "stops_path": "https://zenodo.org/record/17778363/files/stops.txt?download=1"
  },
  "demographic_dict": {
    "INDEX POPULATION 2019[1]": "pop_2019",
    "RANK 2019[3] ": "RANK_2019",
    ' CLUSTER 2019[4] ': "socioeco_2019",
    "שם יישוב": "name_hebrew",
    "NAME OF LOCALITY": "name_english"
  },
  "demographic_columns": [
    "pop_2019",
    "RANK_2019",
    "socioeco_2019",
    "name_hebrew",
    "name_english",
    "YISHUV_STAT11",
    "CODE OF LOCALITY"
  ],
  "rishui_dict": {
    "מחוז": "eastwest",
    "מקט": "routeid",
    "סוג קו": "line_type",
    "כיוון": "direction",
    "חלופה": "alternative",
    "שם סוג שירות": "service_type",
    "אורך מסלול": "route_length",
    "ייחודיות הקו": "exclusivity"
  },
  "service_type_dict": {
    "בינעירוני-מהיר": 1,
    "בינעירוני-מאסף": 1,
    "אזורי-מאסף": 2,
    "עירוני-עירוני עורקי מאסף": 3,
    "עירוני-מקומי מאסף": 3
  },
  "time_periods": {
    "morning_begin": "06:00:00",
    "noon_begin": "09:00:00",
    "afternoon_begin": "15:00:00",
    "evening_begin": "19:00:00"
  },
  "git_dict": {
    "change has been made": 1
  },
  "name_dict": {
    "eastwest": "East_JLM_lines",
    "type": "service_types",
    "socioeco_2019": "Socioeconomic_ranking",
    "updated_ultraorthodox_percent": "Ultraorthodox_buses",
    "directness": "Directness_measurements",
    "settlements": "Settlements_lines",
    "west": "West_metropolin_lines",
    "injlm": "InJerusalem_lines",
    "headway": "Lines_headway",
    "not_intact_percent": "percent_problematic_trips"
  },
  "general_columns": [
    "East_JLM_lines",
    "service_types",
    "Socioeconomic_ranking",
    "Ultraorthodox_buses",
    "Directness_measurements",
    "Settlements_lines",
    "West_metropolin_lines",
    "InJerusalem_lines",
    "percent_problematic_trips",
    "number_of_complaints",
    "passengersnumber_thousands"
  ]
}
