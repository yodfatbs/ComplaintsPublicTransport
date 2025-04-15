import arcpy 
arcpy.env.overwriteOutput=True
arcpy.env.workspace="gis/main_map/main_map.gdb"

import pandas as pd
import numpy as np


# from dicts import *
from general_functions import to_df, seperate_routeid_direction_alternative
from dicts import GIS, Links

layers = GIS['gis_layers']
fields_names = GIS['gis_fields_and_names']

buses_links=Links['buses_links']


def calculate_socio_eco_per_stop():
    """ 
    function makes: layer of bus stops inside jlm metro, each has demogrphic data
    """
    select_stops_in_jlm_metro = arcpy.SelectLayerByLocation_management(in_layer=layers['stops_from_GTFS'], #only stops in jlm metro area
                                                                       overlap_type="WITHIN", 
                                                                       select_features=layers['jlm_metro']) 
    
     # give bus stops a socio-economic ranking based on location
    arcpy.CopyFeatures_management(in_features=select_stops_in_jlm_metro, 
                                  out_feature_class=fields_names['stop_in_jlm_metro'])

    #give socio eco record to stops if they are inside a statistical area
    arcpy.analysis.SpatialJoin(target_features=fields_names['stop_in_jlm_metro'], 
                               join_features="sa_including_settlements", 
                               out_feature_class='select_1st_step',
                               match_option='INTERSECT')

    #seperate between dots inside statistical areas and these which are not
    arcpy.analysis.Select('select_1st_step', "outside_sa", '"STAT11" IS NULL')
    arcpy.analysis.Select('select_1st_step', "inside_sa", '"STAT11" IS NOT NULL')
    arcpy.management.Delete('select_1st_step')

    #delete fields from the spatial join
    outside = [field.name for field in arcpy.ListFields('outside_sa')]
    all = [field.name for field in arcpy.ListFields(fields_names['stop_in_jlm_metro'])]
    to_keep=[field for field in outside if field  in all]
    arcpy.management.DeleteField('outside_sa', to_keep, "KEEP_FIELDS")

    #give socio eco record to stops based on proxmity statistical area
    arcpy.analysis.SpatialJoin('outside_sa', "sa_including_settlements", 
                               'outside_sa_closest',match_option='CLOSEST')

    #merge the dots together and delete the spare layers
    arcpy.Merge_management(['outside_sa_closest', 'inside_sa'], fields_names['stops_jlm_layer_name'])
    arcpy.management.Delete('outside_sa')
    arcpy.management.Delete('outside_sa_closest')
    arcpy.management.Delete('inside_sa')

    ###########################################################################################
    ###########################################################################################
def match_stops_to_bus_route(bus_lines_jlm):
    """ 
    function gets: layer of bus lines belongs to JLM metropolin 
    function returns: df of buses and their's bus stops 
    """
    #take lines and stations from the extraction from NPDA DB
    lines_stops=pd.read_excel(buses_links['NPTA_extractions'],sheet_name='rb_stations_length') 

    # create route_desc and routeid_direction columns
    lines_stops['route_desc']=lines_stops['OfficeLineId'].astype(str)\
          +'-'+ lines_stops['Direction'].astype(str)+'-'+lines_stops['LineAlternative'].astype(str)
    lines_stops['routeid_direction']=lines_stops['OfficeLineId'].astype(str)+'-'+ lines_stops['Direction'].astype(str)

    #organize table
    lines_stops.drop(columns=['trip_km_fact'], inplace=True)
    lines_stops.drop_duplicates(inplace=True)
    lines_stops.rename(columns={'StationId':'stop_code'},inplace=True)

    #dataframe of the relevant buses
    stop_route_jlm=lines_stops[lines_stops['route_desc'].isin(
        bus_lines_jlm['route_desc'])].drop_duplicates() 

    return stop_route_jlm
    ###########################################################################################
    ###########################################################################################

def calculate_socio_eco_per_line(stop_route_jlm):    
    """ 
    function gets: df of buses and their's bus stops 
    function returns: clean df of buses and their's bus stops with demographic data
    """

#calculate socio eco of each stop in jlm metro based on proximity to SA
    stops_in_jlm=to_df(fields_names['stops_jlm_layer_name'])

    stops_in_jlm=stops_in_jlm[
        (stops_in_jlm['Main_Function_Code']==1)&(~stops_in_jlm['Pop_Total'].isnull())]#include only stops in residential areas
    
    # cleam df
    stops_in_jlm=stops_in_jlm[['stop_code','socioeco_2019','updated_ultraorthodox_percent']].copy()
    stops_in_jlm['stop_code']=stops_in_jlm['stop_code'].astype(int)

    # merge each line to it's bus stops
    socio_validations_residential=pd.merge(stop_route_jlm, stops_in_jlm, on='stop_code', how='left') #combine lines with stops

    return socio_validations_residential

    ###########################################################################################
    ###########################################################################################

def passengers_number_per_stop():
    """ 
    function returns: number of passengers per line and bus stop in the research period
    """
    #import validation in stops by line data
    stops_olim=pd.read_excel(buses_links['NPTA_extractions'], sheet_name='validation_by_stationline') 
    stops_olim['makat']=stops_olim['officelineid'
                                ].astype(str)+'-'+stops_olim['direction'].astype(str)+'-'+stops_olim['linealternative'].astype(str)
    stops_olim=stops_olim[~stops_olim['stationorder'].isna()] #exclude unassigned validations
    stops_olim=stops_olim[['makat','stationid','stationorder','passengersnumber']]

    #import stops by line data
    rb_lines=pd.read_excel(buses_links['NPTA_extractions'], sheet_name='rb_stations_length') 
    rb_lines['makat']=rb_lines['OfficeLineId'
                                ].astype(str)+'-'+rb_lines['Direction'].astype(str)+'-'+rb_lines['LineAlternative'].astype(str)
    
    #organize data
    rb_lines.drop(columns=['trip_km_fact'], inplace=True)
    rb_lines.drop_duplicates(inplace=True)
    rb_lines.rename(columns = {'StationOrder':'stationorder','StationId':'stationid'}, inplace = True) 

    #for each stop in route present number of passengers, add total passengers for route
    rb_olim=pd.merge(rb_lines,stops_olim, on =('makat','stationid','stationorder'), how='inner')
    rb_olim.rename(columns = {'stationorder':'StationOrder','stationid':'stop_code','makat':'route_desc'}, inplace = True) 

    return rb_olim[['route_desc', 'StationOrder', 'stop_code', 'passengersnumber']]

    ###########################################################################################
    ###########################################################################################

def calulate_weighted_mean_per_stop(ranked_lines, passengers_in_stops):
    """ 
    gunction gets: clean df of buses and their's bus stops with demographic data,
        number of passengers per line and bus stop in the research period
    function returns: df of demographic data, and part of passengers in each stop for each trip
    """
    #merge demographic data with validations data
    socio_eco_validations=pd.merge(ranked_lines, passengers_in_stops,
                                    on=['route_desc', 'StationOrder', 'stop_code'], how='left')
    
    #include only stops in residential areas
    residential_copy=socio_eco_validations[
        (~socio_eco_validations['updated_ultraorthodox_percent'].isna())
        &
        (~socio_eco_validations['socioeco_2019'].isna())
        ].copy()

    # find sum of passengers per line
    residential_copy['all_passengers']=residential_copy.groupby('route_desc')['passengersnumber'].transform('sum') 

    #calculate passengers's percent in each stop
    residential_copy['olim_percent']=residential_copy['passengersnumber']/residential_copy['all_passengers'] 

    residential_copy.fillna({'passengersnumber':0,'all_passengers':0,'olim_percent':0}, inplace=True)
    return residential_copy

    ###########################################################################################
    ###########################################################################################

def grouped_weighted_avg(socio_validations_residential): 
    """ 
    function makes: calculate weighted average by the passengers percent in each stop. 
        for lines with less than 10 validations, use only the demographic data
    function gets: dataframe of busstops, each with socio economic data, and number of validations in each 
    function returns: dataframe of lines with socio eco ranking based on passengers percent in stations
    """
    #seperate lines with and without validations
    no_validations=socio_validations_residential[socio_validations_residential['all_passengers']<=10].copy() 
    with_validations=socio_validations_residential[socio_validations_residential['all_passengers']>10].copy()

    #calculate average/wighted average for each line demographic properties
    func_dict={"socioeco_2019": "mean",
               "updated_ultraorthodox_percent": "mean"} #the kind of calculations
    
    #function for weighted mean
    cols = ['socioeco_2019','updated_ultraorthodox_percent'] 
    def w_avg(g, cols): 
        return round(pd.Series(np.average(g[cols], weights=g['olim_percent'], axis=0),
                        index=cols), 2)

    group_with_validations=with_validations.groupby('route_desc', as_index=False).apply(w_avg, cols)
    group_no_validations=no_validations.groupby(['route_desc'], as_index=False 
                                                ).agg(func_dict).round(2)
    socio_eco_res12=pd.concat([group_no_validations,group_with_validations])
    
    return socio_eco_res12[['route_desc','socioeco_2019','updated_ultraorthodox_percent']]

    ###########################################################################################
    ###########################################################################################

def socio_eco_resolution3(socio_eco_res12):
    """ 
    function makes: transfers coxio eco data to resolution 3 - routeid-direction 
    function gets:  dataframe of lines with socio eco ranking based on passengers percent in stations
    function returns:  dataframe of routeid-directions with socio eco ranking based on passengers percent in stations
    """
    grouped_weighted_avg=seperate_routeid_direction_alternative(socio_eco_res12)

    agg={'socioeco_2019':'mean',
         'updated_ultraorthodox_percent':'mean'}
    socio_eco_res3=grouped_weighted_avg.groupby('routeid_direction', as_index=False).agg(agg)


    return socio_eco_res3

    ###########################################################################################
    ###########################################################################################

def calculate_socio_econimoc_lines(bus_lines_jlm):
    """
    function returns: df of relevand bus lines with their ranking of socio economic ranking
    """
    calculate_socio_eco_per_stop()
    stop_route_jlm=match_stops_to_bus_route(bus_lines_jlm)
    ranked_lines=calculate_socio_eco_per_line(stop_route_jlm)
    passengers_in_stops=passengers_number_per_stop()
    mean_per_stop=calulate_weighted_mean_per_stop(ranked_lines, passengers_in_stops)
    res_12=grouped_weighted_avg(mean_per_stop)
    res3=socio_eco_resolution3(res_12)

    print ('sosio economic ranking printed')
    return res_12, res3