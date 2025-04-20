# cbs_links={'demographic_urb_path':"external_files/cbs_files/socio_eco_urb.xlsx",
#                 'demographic_reg_path':"external_files/cbs_files/socio_eco_regional.xlsx",
#                 'demographic_sub_path':"external_files/cbs_files/socio_eco_suburb.xlsx",
#                 'ultraorthodox_path':"external_files/cbs_files/ultraorthodox_state.xlsx"}


# buses_links = {'rishui_lines':"external_files/transportation_ministry/rishui_lines.xlsx",
#                'NPTA_extractions':"external_files/transportation_ministry/extract_npta_060324.xlsx",
#                'comlaints':"external_files/transportation_ministry/public complaints jan22-jun 23.xlsx"
# }

# GTFS_links = {'stops_path':'external_files/GTFS_files_june_23/stops.txt',
# }

# # Demographic
# demographic_dict={'INDEX POPULATION 2019[1]':'pop_2019',
#                                  'RANK 2019[3] ':'RANK_2019',
#                                   ' CLUSTER 2019[4] .1':'socioeco_2019',
#                                   'שם יישוב':'name_hebrew',
#                                   'NAME OF LOCALITY':'name_english'}

# demographic_columns=['pop_2019','RANK_2019','socioeco_2019','name_hebrew','name_english','YISHUV_STAT11','CODE OF LOCALITY']

# # rishui
# rishui_dict={'מחוז':'eastwest'
#         ,'מקט':'routeid',
#         'סוג קו':'line_type',
#         'כיוון':'direction',
#             'חלופה':'alternative',
#             'שם סוג שירות':'service_type',
#                 'אורך מסלול':'route_length',
#                 'ייחודיות הקו':'exclusivity'}

# service_type_dict={'בינעירוני-מהיר':1,
#                 'בינעירוני-מאסף':1,
#                     'אזורי-מאסף':2,
#                     'עירוני-עירוני עורקי מאסף':3,
#                     'עירוני-מקומי מאסף':3}

# #ebitzua
# time_periods = {'morning_begin':'06:00:00',
#                 'noon_begin':'09:00:00',
#                 'afternoon_begin':'15:00:00',
#                 'evening_begin':'19:00:00'}

# git_dict = {'change has been made':1}


# # export dicts
# name_dict={'eastwest':'East_JLM_lines', 
#     'type': 'service_types', 
# 'socioeco_2019':'Socioeconomic_ranking', 
# 'updated_ultraorthodox_percent':'Ultraorthodox_buses',
# 'directness':'Directness_measurements', 
# 'settlements': 'Settlements_lines', 
# 'west':'West_metropolin_lines', 
# 'injlm':'InJerusalem_lines',
# 'headway':'Lines_headway', 
# 'not_intact_percent':'percent_problematic_trips'
# }

# general_columns=['East_JLM_lines', 'service_types', 
#     'Socioeconomic_ranking', 'Ultraorthodox_buses',
#     'Directness_measurements', 'Settlements_lines',
#     'West_metropolin_lines', 'InJerusalem_lines',
#     'percent_problematic_trips', 'number_of_complaints',
#     'passengersnumber_thousands']



GIS={
  "gis_layers": {
    "occupation": "external_files/gis_layers/governmental_layers.gdb/occupation",
    "jlm_boundry": "external_files/gis_layers/governmental_layers.gdb/jlm_boundry",
    "jlm_metro": "external_files/gis_layers/governmental_layers.gdb/jlm_metro",
    "statisticalareas_2022": "external_files/gis_layers/governmental_layers.gdb/sa_2022",
    "jlm_city_boundries": "external_files/gis_layers/governmental_layers.gdb/jlm_boundry",
    "settlements": "external_files/gis_layers/settlements/settlements.shp",
    "original_bus_layer": "external_files/gis_layers/governmental_layers.gdb/bus_routes",
    "stops_from_GTFS": "external_files/gis_layers/governmental_layers.gdb/stops" 
  },
  "gis_fields_and_names": {
    "copy_bus_layer": "copy_buses",
    "JLM_buses_clip": "bus_routes_calculate",
    "jlm_city_boundries": "external_files/gis_layers/governmental_layers.gdb/jlm_boundry",
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
    "demographic_urb_path": "external_files/cbs_files/socio_eco_urb.xlsx",
    "demographic_reg_path": "external_files/cbs_files/socio_eco_regional.xlsx",
    "demographic_sub_path": "external_files/cbs_files/socio_eco_suburb.xlsx",
    "ultraorthodox_path": "external_files/cbs_files/ultraorthodox_state.xlsx"
  },
  "buses_links": {
    "rishui_lines": "external_files/transportation_ministry/rishui_lines.xlsx",
    "NPTA_extractions": "external_files/transportation_ministry/extract_npta_060324.xlsx",
    "comlaints": "external_files/transportation_ministry/public complaints jan22-jun 23.xlsx"
  },
  "GTFS_links": {
    "stops_path": "external_files/GTFS_files_june_23/stops.txt"
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
