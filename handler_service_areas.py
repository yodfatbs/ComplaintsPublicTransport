from config_arcpy import *
from config_general import *
from general_functions import *

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
    df_part.rename(columns={"route_desc": "makat"}, inplace=True)
    
    return df_part.drop_duplicates()
###########################################################################################
###########################################################################################

def create_service_areas(service_area):
    if service_area=='west_netropolitan_area': #for west metropolin lines
        arcpy.analysis.Union([occupation, jlm_boundry], "unioned") #union jerusalem and west bank
        arcpy.analysis.Erase(jlm_metro, 'unioned', 'clipper') #exclude the west metropolitan area
    elif service_area=='West_Bank_Settlements':
        arcpy.analysis.Erase(occupation,jlm_boundry, 'clipper') #exclude from west bank area the east jerusaelm area
        
###########################################################################################
###########################################################################################

def calculate_line_percent_within_sevice_area(outfieldname,layer_name='temp',final_bus_layer='bus_routes_jlm_metro'):
    #calculate whole route length
    arcpy.management.CopyFeatures(final_bus_layer, layer_name)#feature  for calculation
    calculate_route_length(layer_name,'Shape_Length','whole_route_length_km')#calculate whole route length 

    #calculate route length inside area
    arcpy.analysis.Clip(layer_name, 'clipper','clipped_middle' ) # clip routes inside jlm  boundry
    calculate_route_length('clipped_middle','Shape_Length','clipped_route_km')#calculate clipped route length 

    #join whole and clipped length
    arcpy.management.JoinField(layer_name, 'route_desc', 'clipped_middle',
                                'route_desc', 'clipped_route_km') 
    
    # Fix none values to 0
    arcpy.management.AddField(layer_name, outfieldname, "FLOAT")
    with arcpy.da.UpdateCursor(layer_name, ['clipped_route_km']) as cursor:
        for row in cursor:
            if row[0] is None:
                row[0] = 0
                cursor.updateRow(row)

    # calculate % within area
    percent_inside ="round(100*(float(!{0}!) / float(!{1}!)), 2)".format('clipped_route_km', 'whole_route_length_km')
    arcpy.management.CalculateField(layer_name, outfieldname, percent_inside, "PYTHON3")
    df=to_df(layer_name)
    df=df[df['route_type_text']=='Bus'].copy()

    arcpy.Delete_management(layer_name) 

    return df

###########################################################################################
###########################################################################################

def match_lines_to_service_areas():
    """ 
    function makes: percent of bus routes  to service areas
    function gets: lines rishui data, bus routes layer, outside area polygon for calculation, parts to take from it (jlm borders), 
    calcuated field name, layers to union and take out of measuring polygon if necessary
    function returns: dataframe &csv of lines with percent of route inside occupied territories
    """
    service_areas_df=[]
    service_area_dict={'West_Bank_Settlements':'settlements', 'west_netropolitan_area':'west'}
    for service_area,outfieldname in service_area_dict.items():
        create_service_areas(service_area) #create west bank/west metropolitan areas

        df_process=calculate_line_percent_within_sevice_area(outfieldname)

        # df_process= to_df(layer_name)# return layer of jlm lines
        
        #filter duplications
        df=df_process.groupby(['route_id', 'agency_id', 'route_desc'], as_index=False).agg(
            {'whole_route_length_km':'mean', 
            'jlm_route_length_km':'mean', 
            'percent_inside_jlm':'mean', 
            'clipped_route_km':'mean', 
            outfieldname:'mean'})
        #delete spare layers
        arcpy.Delete_management('clipped_bus_routes_occupation_layer') 
        arcpy.Delete_management('clipped_middle') 
        arcpy.Delete_management('clipper') 
        arcpy.Delete_management('unioned') 
        
        #organize data and take out only necessary columns
        df_res12=seperate_routeid_direction_alternative(df)
        # df_res3=df_res12.groupby('routeid_direction', as_index=False)[outfieldname].mean()

        service_areas_df.append(df_res12[['makat','routeid_direction', outfieldname]])
    return service_areas_df[0], service_areas_df[1]
###########################################################################################
###########################################################################################

def create_in_jlm_lines(final_bus_layer='bus_routes_jlm_metro'):

    lines=to_df(final_bus_layer)

    lines=seperate_routeid_direction_alternative(lines)
    injlm_res12=lines.loc[(lines['route_type_text']=='Bus')][['makat','routeid_direction', 'percent_inside_jlm']].drop_duplicates()


    # injlm_res3=injlm_res12.groupby('routeid_direction', as_index=False)['injlm'].mean()

    return injlm_res12
###########################################################################################
###########################################################################################

def determine_service_area(resolution):
    resolution['settlements']=np.where(resolution['settlements']>=20,1,0)
    resolution['west']=np.where((resolution['west']>=20)&(resolution['settlements']==0),1,0)
    resolution['injlm']=np.where(resolution['percent_inside_jlm']>=0.8,1,0)

    return resolution.drop(columns='percent_inside_jlm')

###########################################################################################
###########################################################################################

def create_service_areas_resolutions(risui_res12):
    settlements_res12,west_metropolin_res12=match_lines_to_service_areas()

    in_jlm_res12=create_in_jlm_lines()
    #create service areas for resolution 1,2

    #merge
    service_areas_12=settlements_res12.merge(west_metropolin_res12, on=['makat', 'routeid_direction'], how='outer')
    service_areas_12=service_areas_12.merge(in_jlm_res12, on=['makat', 'routeid_direction'], how='outer')

    #add east JLM lines
    service_areas_12=service_areas_12.merge(risui_res12[['makat','eastwest']].drop_duplicates(), on='makat', how='inner')
    service_areas_12.loc[service_areas_12['eastwest']==1, 'settlements'] = 0 # settlement line cannot be east jlm line

    res_12=determine_service_area(service_areas_12)

    service_areas_3=service_areas_12.drop(columns='makat').groupby('routeid_direction', as_index=False).mean()

    res3=determine_service_area(service_areas_3)
    print ('service areas are printed')
    return res_12.drop(columns='routeid_direction'), res3



