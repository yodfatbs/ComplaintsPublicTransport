from dicts import GIS, workspace

import arcpy 
arcpy.env.overwriteOutput=True
arcpy.env.workspace=workspace

from general_functions import calculate_route_length, to_df

layers = GIS['gis_layers']
fields_names = GIS['gis_fields_and_names']

###########################################################################################
###########################################################################################

def find_route_length_inside_outside_jlm():
    """
    function makes: GIS layer of all buslines in Israel, with 
      a field of route length inside Jerusalem, and a field with the complete route length
    """
    arcpy.management.CopyFeatures(in_features=layers['original_bus_layer'], 
                                out_feature_class=fields_names['copy_bus_layer'])#feature  for calculation
    #calculate whole route length 
    calculate_route_length(fields_names['copy_bus_layer']
                           ,'Shape_Length',fields_names['whole_route_field'])

    arcpy.analysis.Clip(in_features=fields_names['copy_bus_layer'], # clip routes inside jlm  boundry
                        clip_features=fields_names['jlm_city_boundries'], 
                        out_feature_class=fields_names['JLM_buses_clip'] ) 

    calculate_route_length(fields_names['JLM_buses_clip'],'Shape_Length'
                           ,fields_names['inside_jlm_field'])#calculate clipped route length 

    arcpy.management.JoinField(in_data=fields_names['copy_bus_layer'], #join whole and clipped length
                                in_field='route_desc', 
                                join_table=fields_names['JLM_buses_clip'],
                                join_field='route_desc', 
                                fields=fields_names['inside_jlm_field']) 
    
###########################################################################################
###########################################################################################

def calculate_percent_of_bus_route_inside_jlm():
    """
    function makes: GIS layer with percent of route inside Jerusalem
    """
    # fix None values to zero, for further calculation
    with arcpy.da.UpdateCursor(fields_names['copy_bus_layer'], 
                               [fields_names['inside_jlm_field']]) as cursor:
        for row in cursor:
            if row[0] is None:
                row[0] = 0
                cursor.updateRow(row)

    arcpy.management.AddField(in_table=fields_names['copy_bus_layer'],  # add field for later calculation
                                field_name=fields_names['percent_inside_jlm_field'], 
                                field_type="FLOAT")# Set the name of the field you want to calculate
    
    percent_inside_jlm =f"float(!{fields_names['inside_jlm_field']}!) / float(!{fields_names['whole_route_field']}!)" #calculation formula

    arcpy.management.CalculateField(in_table=fields_names['copy_bus_layer'], #calculate field
                                    field=fields_names['percent_inside_jlm_field'], 
                                    expression=percent_inside_jlm, 
                                    expression_type="PYTHON3")
    
    arcpy.MakeFeatureLayer_management(in_features=fields_names['copy_bus_layer'], #create temporary layer with results
                                        out_layer="TempLayer") 
    
###########################################################################################
###########################################################################################

def set_threshold_and_df():
    """
    function makes: GIS layer contains only bus lines with sufficient percent of route is Jerusalem (25%)
    """
    #determine threshold
    set_threshold = "{} >= {}".format(
        arcpy.AddFieldDelimiters(datasource=fields_names['copy_bus_layer'], 
                                 field=fields_names['percent_inside_jlm_field']), 
                                 fields_names['threshold_value'])
    
    arcpy.SelectLayerByAttribute_management("TempLayer", "NEW_SELECTION", set_threshold)
    arcpy.CopyFeatures_management("TempLayer", fields_names['final_bus_layer'])

    arcpy.Delete_management(fields_names['copy_bus_layer']) 
    arcpy.Delete_management(fields_names['JLM_buses_clip']) 
    arcpy.Delete_management('TempLayer') 

    jlm_buses=to_df(fields_names['final_bus_layer'])
    jlm_buses[['routeid','Direction','Alternative']] = jlm_buses['route_desc'].str.split('-',expand=True)

    return jlm_buses[jlm_buses['route_type_text']=='Bus']# only buses

###########################################################################################
###########################################################################################

def make_jlm_metro_routes():
    """ 
    function makes: add a field with the percentage of bus lines in to JLM metropolin
    function gets: bus lines layer,field name of area inside jlm, field name of whole length, field name of percent inside jlm,
    name of the jlm bus layer, percent of line insided jlm to be considered a part of jlm
    function returns: layer of bus lines inside jlm metro
    """
    try: #fix none values to zero to later calculation

        find_route_length_inside_outside_jlm()

        calculate_percent_of_bus_route_inside_jlm()
        
        df=set_threshold_and_df()

        print('relevant_buses_layer created')
        return df

    except arcpy.ExecuteError:
        print(arcpy.GetMessages())


        