import pandas as pd
import arcpy 
arcpy.env.overwriteOutput=True
arcpy.env.workspace="gis/main_map/main_map.gdb"

from dicts import GIS, Links

fields_names = GIS['gis_fields_and_names']
buses_links=Links['buses_links']

def add_zeros_codoflocality(value):
    """
    add zeros to semel yishuv, to compare it later
    """
    if isinstance(value,str)==False:
        value=value.astype(str)
    if len(value) == 3:
        return value + '0'
    elif len (value)==2:
        return value + '00'
    elif len (value)==1:
        return value + '000'
    else:
        return value
################################
################################
def add_zeros_codofstatistical(value):
    """
    add zeros to statistical are code, to make it comparabl
    """
    if isinstance(value,str)==False:
        value=value.astype(str)
    if len(value) == 3:
        return '0'+ value 
    elif len (value)==2:
        return '00'+value
    elif len (value)==1:
        return '000'+value
    else:
        return value
################################
################################    
def turnzero(value):
    """
    turn value to zero if value is not int/float
    """
    if isinstance(value,float)!=True and isinstance(value,int)!=True:
        return 0
    else:
        return value
    
################################
################################  
def to_df(final_bus_layer):
    jlm_lines_fields = [field.name for field in arcpy.ListFields(final_bus_layer)] #export jlm line list to layer and csv
    jlm_lines_data = [row for row in arcpy.da.SearchCursor(final_bus_layer, jlm_lines_fields)]
    jlm_lines_out=pd.DataFrame(jlm_lines_data, columns=jlm_lines_fields)
    return jlm_lines_out

#################################
#################################

def calculate_route_length(feature,field_to_calculate,new_field_name):
    """ 
    function makes: calculate length of bus line
    function gets: layer to calculate (bus lines), field to calculate (shape length), and new field name (area)
    function returns: new column in layer saying what is the line length
    """
    try:
    # Set the name of the field you want to calculate
        arcpy.management.AddField(feature, new_field_name, "FLOAT")
    # Expression for calculation (e.g., copying values from another field)
        to_km_length = "round(100*!"+field_to_calculate+"!,2)"  # Replace "OtherField" with the actual field name
    # Use CalculateField_management
        arcpy.management.CalculateField(in_table=feature, 
                                        field=new_field_name, 
                                        expression=to_km_length, 
                                        expression_type="PYTHON3",
                                        field_type="FLOAT")
    except arcpy.ExecuteError:
        print(arcpy.GetMessages())

###########################################################################################
###########################################################################################

def seperate_routeid_direction_alternative(df):
    """ 
    function makes: finds wether a bus line is from east jlm, and then exclude it from calculations
    function gets: dataframe of makat and route percent inside research area (west/east to JLM)
    function returns: 2 dataframes, in resolution 12, and 3, of lines with percent of route inside research area (west/east to JLM)
    """

    # clean and orgnaize data
    df_part=df.copy()
    df_part[['routeid','Direction','Alternative']] = df_part['route_desc'].str.split('-',expand=True)
    df_part['routeid_direction'] = df_part['routeid'].astype(str)+'-'+df_part['Direction'] # for resolution 3
    df_part['makat']=df_part['route_desc']
    
    return df_part.drop_duplicates()

###########################################################################################
###########################################################################################

def prepare_data_to_directness_analysis():
    """
    function returns: df of lines and stops, including coordinates and route lengths, for directness analysis.
    for circular lines, only half of the route is considered
    """

    #take lines and stations from the extraction from NPDA DB
    lines_stops_all=pd.read_excel(buses_links['NPTA_extractions'],sheet_name='rb_stations_length') 
    lines_stops_all['route_desc']=lines_stops_all['OfficeLineId'].astype(str) +\
        '-'+ lines_stops_all['Direction'].astype(str)+'-'+lines_stops_all['LineAlternative'].astype(str)
    lines_stops_all.rename(columns={'StationId':'stop_code'},inplace=True)

    #take only lines in jlm
    jlm_lines=to_df(fields_names['final_bus_layer'])
    lines_stops_start=lines_stops_all[lines_stops_all['route_desc'].isin(jlm_lines['route_desc'])]

    #divide between direct and circular lines
    circular_lines=lines_stops_start[lines_stops_start['Direction']==3].copy()
    direct_lines=lines_stops_start[lines_stops_start['Direction']!=3].copy()

    # for circular lines, take only half  route
    circular_lines['middle']=round(circular_lines.groupby('route_desc')['StationOrder'].transform('max')/2,0)
    half_line=circular_lines[(circular_lines['StationOrder']<=circular_lines['middle'])].copy()
    half_line['DistanceFromOriginStation']=round(half_line['DistanceFromOriginStation']/1000, 3)
    half_line['trip_km_fact_up']=half_line.groupby('route_desc')['DistanceFromOriginStation'].transform('max')
    half_line.rename(columns={'trip_km_fact': 'trip_km_fact1'}, inplace=True)
    half_line.rename(columns={'trip_km_fact_up': 'trip_km_fact'}, inplace=True)
    half_line.drop(columns=['trip_km_fact1', 'middle'], inplace=True)
    #concat the now half circular and direct lines
    lines_stops=pd.concat([direct_lines, half_line])[['route_desc','stop_code','StationOrder','trip_km_fact']]

    lines_stops['stop_code']=lines_stops['stop_code'].astype('str')

    #attach geographic stops data
    stops=to_df(fields_names['stops_jlm_layer_name'])[['stop_code','stop_name','stop_lat', 'stop_lon']] 
    stop_route_all= pd.merge(lines_stops, stops, on='stop_code', how='inner')
    stop_route_all.to_csv('outputs/direcness_measurement.csv')
    print ('pre directness analysis complete')
    return 

###########################################################################################
###########################################################################################

def create_directness():
    directness=pd.read_csv('outputs/final_directness.csv')
    directness_res12=directness[['route_desc', 'directness']].copy()

    directness[['routeid','Direction','Alternative']] = directness['route_desc'].str.split('-',expand=True)
    directness['routeid_direction']=directness['routeid'].astype(str)+'-'+directness['Direction'].astype(str)
    directness_res3=directness.groupby('routeid_direction', as_index=False)['directness'].mean()
    return directness_res12, directness_res3