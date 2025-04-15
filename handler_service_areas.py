import arcpy 
import numpy as np
arcpy.env.overwriteOutput=True
arcpy.env.workspace="gis/main_map/main_map.gdb"

from general_functions import calculate_route_length, to_df, seperate_routeid_direction_alternative
from dicts import GIS

layers = GIS['gis_layers']
fields_names = GIS['gis_fields_and_names']

###########################################################################################
###########################################################################################

def create_service_areas(service_area):
    if service_area=='west_netropolitan_area': #for west metropolin lines
        arcpy.analysis.Union([layers['occupation'], layers['jlm_boundry']], "unioned") #union jerusalem and west bank
        arcpy.analysis.Erase(layers['jlm_metro'], 'unioned', 'clipper') #exclude the west metropolitan area
    elif service_area=='West_Bank_Settlements':
        arcpy.analysis.Erase(layers['occupation'],layers['jlm_boundry'], 'clipper') #exclude from west bank area the east jerusaelm area
        
###########################################################################################
###########################################################################################

def calculate_line_percent_within_sevice_area(outfieldname,
                                              final_bus_layer=fields_names['final_bus_layer'],
                                              layer_name='temp'):
    #calculate whole route length
    arcpy.management.CopyFeatures(final_bus_layer, layer_name)#feature  for calculation
    calculate_route_length(layer_name,'Shape_Length',fields_names['whole_route_field'])#calculate whole route length 

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
    percent_inside ="round(100*(float(!{0}!) / float(!{1}!)), 2)".format('clipped_route_km', fields_names['whole_route_field'])
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
            {fields_names['whole_route_field']:'mean', 
            fields_names['inside_jlm_field']:'mean', 
            fields_names['percent_inside_jlm_field']:'mean', 
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

def create_in_jlm_lines(final_bus_layer=fields_names['final_bus_layer']):

    lines=to_df(final_bus_layer)

    lines=seperate_routeid_direction_alternative(lines)
    injlm_res12=lines.loc[(lines['route_type_text']=='Bus')][
        ['makat','routeid_direction', 'percent_inside_jlm']].drop_duplicates()


    # injlm_res3=injlm_res12.groupby('routeid_direction', as_index=False)['injlm'].mean()

    return injlm_res12
###########################################################################################
###########################################################################################

def determine_service_area(resolution):
    resolution['settlements']=np.where(resolution['settlements']>=20,1,0)
    resolution['west']=np.where((resolution['west']>=20)&(resolution['settlements']==0),1,0)
    resolution['injlm']=np.where(resolution['percent_inside_jlm']>=0.8,1,0)
    resolution.drop(columns='percent_inside_jlm', inplace=True)
    resolution.drop_duplicates(inplace=True)
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
    service_areas_3=service_areas_12.drop(columns='makat').groupby('routeid_direction', as_index=False).mean()

    determine_service_area(service_areas_12)
    determine_service_area(service_areas_3)


    print ('service areas are printed')
    return service_areas_12.drop(columns='routeid_direction'), service_areas_3



