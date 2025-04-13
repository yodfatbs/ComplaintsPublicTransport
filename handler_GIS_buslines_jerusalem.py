
from config_arcpy import *



import arcpy 
arcpy.env.overwriteOutput=True
arcpy.env.workspace="gis/main_map/main_map.gdb"

from general_functions import calculate_route_length, to_df


###########################################################################################
###########################################################################################

def find_route_length_inside_outside_jlm():
    """
    function makes: GIS layer of all buslines in Israel, with 
      a field of route length inside Jerusalem, and a field with the complete route length
    """
    arcpy.management.CopyFeatures(in_features=original_bus_layer, 
                                out_feature_class=copy_bus_layer)#feature  for calculation
    #calculate whole route length 
    calculate_route_length(copy_bus_layer,'Shape_Length',whole_route_field)

    arcpy.analysis.Clip(in_features=copy_bus_layer, # clip routes inside jlm  boundry
                        clip_features=jlm_city_boundries, 
                        out_feature_class=JLM_buses_clip ) 

    calculate_route_length(JLM_buses_clip,'Shape_Length',inside_jlm_field)#calculate clipped route length 

    arcpy.management.JoinField(in_data=copy_bus_layer, #join whole and clipped length
                                in_field='route_desc', 
                                join_table=JLM_buses_clip,
                                join_field='route_desc', 
                                fields=inside_jlm_field) 
    
###########################################################################################
###########################################################################################

def calculate_percent_of_bus_route_inside_jlm():
    """
    function makes: GIS layer with percent of route inside Jerusalem
    """
    # fix None values to zero, for further calculation
    with arcpy.da.UpdateCursor(copy_bus_layer, [inside_jlm_field]) as cursor:
        for row in cursor:
            if row[0] is None:
                row[0] = 0
                cursor.updateRow(row)

    arcpy.management.AddField(in_table=copy_bus_layer,  # add field for later calculation
                                field_name=percent_inside_jlm_field, 
                                field_type="FLOAT")# Set the name of the field you want to calculate
    
    percent_inside_jlm =f"float(!{inside_jlm_field}!) / float(!{whole_route_field}!)" #calculation formula

    arcpy.management.CalculateField(in_table=copy_bus_layer, #calculate field
                                    field=percent_inside_jlm_field, 
                                    expression=percent_inside_jlm, 
                                    expression_type="PYTHON3")
    
    arcpy.MakeFeatureLayer_management(in_features=copy_bus_layer, #create temporary layer with results
                                        out_layer="TempLayer") 
    
###########################################################################################
###########################################################################################

def set_threshold_and_df():
    """
    function makes: GIS layer contains only bus lines with sufficient percent of route is Jerusalem (25%)
    """
    #determine threshold
    set_threshold = "{} >= {}".format(
        arcpy.AddFieldDelimiters(datasource=copy_bus_layer, 
                                 field=percent_inside_jlm_field), 
                                 threshold_value)
    
    arcpy.SelectLayerByAttribute_management("TempLayer", "NEW_SELECTION", set_threshold)
    arcpy.CopyFeatures_management("TempLayer", final_bus_layer)

    arcpy.Delete_management(copy_bus_layer) 
    arcpy.Delete_management(JLM_buses_clip) 
    arcpy.Delete_management('TempLayer') 

    jlm_buses=to_df(final_bus_layer)
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
        return df

    except arcpy.ExecuteError:
        print(arcpy.GetMessages())


        