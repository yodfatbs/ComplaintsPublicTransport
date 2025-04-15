# from dicts import GIS_links

import arcpy 
arcpy.env.overwriteOutput=True
arcpy.env.workspace="gis/main_map/main_map.gdb"

from dicts import GIS

layers = GIS['gis_layers']
fields_names = GIS['gis_fields_and_names']


def create_demographic_sa():
    """ 
    function makes: statistical areas of JLM metropolin GIS layer. uses the existing layers 'statisticalareas_2022','jlm_metro'
    function gets: name of future sa layer, and location of table with demographic data (ultraorthodox percent, and social economic scale)
    function returns: GIS layer with statistical areas of JLM metripolin, for each an ultraorthodox percent and socio-economic scale
    This is only for non-settlements. the next function shall be for that
    """
    #select stat area inside jlm and save as temporary table
    Select_sa_in_jlm = arcpy.SelectLayerByLocation_management(
        layers['statisticalareas_2022'], "WITHIN",layers['jlm_metro']) 
    arcpy.CopyFeatures_management(Select_sa_in_jlm, "sa_without_settlements") 
    #1.
    arcpy.conversion.TableToTable("outputs/demographic_table.csv", 
                                arcpy.env.workspace, "demographic_table") #join geographic+demographic layer
    #2. join demographic data to statistical areas
    fields=['socioeco_2019','pop_2019','RANK_2019','updated_ultraorthodox_percent','arabs'] #fields to join
    arcpy.management.JoinField(in_data="sa_without_settlements", 
                               in_field='YISHUV_STAT11', 
                               join_table='demographic_table',  
                               join_field='YISHUV_STAT11', 
                               fields=fields)
    arcpy.Delete_management("demographic_table") #delete  temporary table
###########################################
def add_settlements_data():
    """ 
    function makes: statistical areas of JLM metropolin GIS layer including settlements
    function gets: sa layer from previous function,  location of table with demographic data and layer of osm (for real shape of settlements)
    function returns: GIS layer with statistical areas of JLM metripolin and demographic data, including settlements
    This is only for non-settlements. the next function shall be for that
    """
## SA layer
    arcpy.CopyFeatures_management("sa_without_settlements",'sa_including_settlements')
    arcpy.AddField_management('sa_including_settlements', "IntegerArea", "LONG") # Add a new field to store the integer area

    # Create an update cursor to calculate and update the integer area
    with arcpy.da.UpdateCursor('sa_including_settlements', ["SHAPE@AREA", 'IntegerArea']) as cursor: 
        for row in cursor:
            area = row[0] # Get the area value
            int_area = int(area) # Convert the area to an integer
            row[1] = int_area # Update the new field with the integer area
            cursor.updateRow(row)
    settlements_query='"IntegerArea"<7900'#take settlements - matked as small dot the size of 7900
    arcpy.MakeFeatureLayer_management('sa_including_settlements', "TempLayer") #create temporary table for calculations of settlement area
    arcpy.SelectLayerByAttribute_management('TempLayer', "NEW_SELECTION", settlements_query)#select settlements and create new int field to update
    #create settlements layer inside GDB
    arcpy.conversion.FeatureClassToFeatureClass(layers['settlements'], arcpy.env.workspace, 'settlements_inprogress') 
    #dissolve different parts of settlements into one
    arcpy.management.Dissolve('settlements_inprogress', 'settlements', ["NAME_NAME"]) 

    # Create an update cursor for the input feature class
    fields = ["SHAPE@", "Shem_Yishuv"]  # Update with the necessary fields

     # update shape of settlements in SA layer according to settlement layer (by name)
    with arcpy.da.UpdateCursor('TempLayer', fields) as cursor:
        for row in cursor: 
            name_to_match = row[1]
            query = "NAME_NAME = '{}'".format(name_to_match)
            with arcpy.da.SearchCursor("settlements", ["SHAPE@"], where_clause=query) as search_cursor:
                for search_row in search_cursor:
                    # Update the geometry of the input feature
                    row[0] = search_row[0]
                    cursor.updateRow(row)

    #delete unnecessary layers                
    arcpy.Delete_management("TempLayer")
    arcpy.Delete_management("settlements_inprogress") 
    arcpy.Delete_management('sa_without_settlements') 
    arcpy.Delete_management('settlements') 

    print('statistical areas with demographic date is printed')

###########################################
###########################################

def build_GIS_demographic_data():
    """ 
    function makes: runs all the above functions
    """

    # create_basic_layers()
    create_demographic_sa()
    add_settlements_data()
    