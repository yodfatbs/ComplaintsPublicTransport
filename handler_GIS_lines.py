from config_arcpy import *

from general_functions import to_df


###########################################################################################    
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

def line_percentage_in_JLM(feature,
                            inside_jlm_field,
                            whole_route_field,
                            percent_inside_jlm_field,
                            final_bus_layer,
                            threshold_value):
    """ 
    function makes: add a field with the percentage of bus lines in  JLM metropolin
    function gets: bus lines layer,field name of area inside jlm, field name of whole length, field name of percent inside jlm,
    name of the jlm bus layer, percent of line insided jlm to be considered a part of jlm
    function returns: layer of bus lines inside jlm metro
    """
    try:
        with arcpy.da.UpdateCursor(feature, [inside_jlm_field]) as cursor:
            for row in cursor:
                if row[0] is None:
                    row[0] = 0
                    cursor.updateRow(row)
        arcpy.management.AddField(feature, percent_inside_jlm_field, "FLOAT")# Set the name of the field you want to calculate
        percent_inside_jlm ="float(!{0}!) / float(!{1}!)".format(inside_jlm_field, whole_route_field)
        arcpy.management.CalculateField(feature, percent_inside_jlm_field, percent_inside_jlm, "PYTHON3")
        arcpy.MakeFeatureLayer_management(feature, "TempLayer")

        set_threshold = "{} >= {}".format(arcpy.AddFieldDelimiters(feature, percent_inside_jlm_field), threshold_value)
        arcpy.SelectLayerByAttribute_management("TempLayer", "NEW_SELECTION", set_threshold)
        arcpy.CopyFeatures_management("TempLayer", final_bus_layer)
    except arcpy.ExecuteError:
        print(arcpy.GetMessages())
    # finally:
    #     arcpy.Delete_management("TempLayer")       

###########################################################################################
###########################################################################################
def Lines_in_JLM_metropolin(threshold_value):
    """ 
    function makes: layer of bus lines belongs to JLM metropolin
    function gets: name of the jlm bus layer, percent of line insided jlm to be considered a part of jlm
    function returns: csv of lines in JLM, layer of bus lines inside jlm metro  
    """
    arcpy.management.CopyFeatures('bus_routes_from_GTFS', 'bus_routes_calculate')#feature  for calculation
    calculate_route_length('bus_routes_calculate','Shape_Length','whole_route_length_km')#calculate whole route length 

    arcpy.analysis.Clip('bus_routes_calculate', 'jlm_city_boundries','clipped_bus_routes_inside_jlm' ) # clip routes inside jlm  boundry
    calculate_route_length('clipped_bus_routes_inside_jlm','Shape_Length','jlm_route_length_km')#calculate clipped route length 

    arcpy.management.JoinField('bus_routes_calculate', 'route_desc', 'clipped_bus_routes_inside_jlm',
                                'route_desc', 'jlm_route_length_km') #join whole and clipped length
    
    line_percentage_in_JLM(feature='bus_routes_calculate',
                           inside_jlm_field='jlm_route_length_km',
                           whole_route_field='whole_route_length_km',
                           percent_inside_jlm_field='percent_inside_jlm',
                          final_bus_layer='bus_routes_jlm_metro',
                          threshold_value=threshold_value) # take only routes that inside jlm according to threshold value
    
    arcpy.Delete_management('bus_routes_calculate') 
    arcpy.Delete_management('clipped_bus_routes_inside_jlm') 
    
    #export jlm line list to layer and csv
    jlm_lines_out=to_df('bus_routes_jlm_metro')
    jlm_lines_out[['routeid','Direction','Alternative']] = jlm_lines_out['route_desc'].str.split('-',expand=True)
    jlm_lines=jlm_lines_out.loc[jlm_lines_out['route_type_text']=='Bus'].copy()
    

    print('JLM metropolitan lines list and layer are printed')

    return jlm_lines# return layer of jlm lines
