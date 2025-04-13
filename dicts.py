cbs_links={'demographic_urb_path':"external_files/cbs_files/socio_eco_urb.xlsx",
                'demographic_reg_path':"external_files/cbs_files/socio_eco_regional.xlsx",
                'demographic_sub_path':"external_files/cbs_files/socio_eco_suburb.xlsx",
                'ultraorthodox_path':"external_files/cbs_files/ultraorthodox_state.xlsx"}


buses_links = {'rishui_lines':"external_files/transportation_ministry/rishui_lines.xlsx",
               'NPTA_extractions':"external_files/transportation_ministry/extract_npta_060324.xlsx",
               'comlaints':"external_files/transportation_ministry/public complaints jan22-jun 23.xlsx"
}

GTFS_links = {'stops_path':'external_files/GTFS_files_june_23/stops.txt',
}

# Demographic
demographic_dict={'INDEX POPULATION 2019[1]':'pop_2019',
                                 'RANK 2019[3] ':'RANK_2019',
                                  ' CLUSTER 2019[4] .1':'socioeco_2019',
                                  'שם יישוב':'name_hebrew',
                                  'NAME OF LOCALITY':'name_english'}

demographic_columns=['pop_2019','RANK_2019','socioeco_2019','name_hebrew','name_english','YISHUV_STAT11','CODE OF LOCALITY']

# rishui
rishui_dict={'מחוז':'eastwest'
        ,'מקט':'routeid',
        'סוג קו':'line_type',
        'כיוון':'direction',
            'חלופה':'alternative',
            'שם סוג שירות':'service_type',
                'אורך מסלול':'route_length',
                'ייחודיות הקו':'exclusivity'}

service_type_dict={'בינעירוני-מהיר':1,
                'בינעירוני-מאסף':1,
                    'אזורי-מאסף':2,
                    'עירוני-עירוני עורקי מאסף':3,
                    'עירוני-מקומי מאסף':3}

#ebitzua
time_periods = {'morning_begin':'06:00:00',
                'noon_begin':'09:00:00',
                'afternoon_begin':'15:00:00',
                'evening_begin':'19:00:00'}

git_dict = {'change has been made':1}


# export dicts
name_dict={'eastwest':'East_JLM_lines', 
    'type': 'service_types', 
'socioeco_2019':'Socioeconomic_ranking', 
'updated_ultraorthodox_percent':'Ultraorthodox_buses',
'directness':'Directness_measurements', 
'settlements': 'Settlements_lines', 
'west':'West_metropolin_lines', 
'injlm':'InJerusalem_lines',
'headway':'Lines_headway', 
'not_intact_percent':'percent_problematic_trips'
}

general_columns=['East_JLM_lines', 'service_types', 
    'Socioeconomic_ranking', 'Ultraorthodox_buses',
    'Directness_measurements', 'Settlements_lines',
    'West_metropolin_lines', 'InJerusalem_lines',
    'percent_problematic_trips', 'number_of_complaints',
    'passengersnumber_thousands']
