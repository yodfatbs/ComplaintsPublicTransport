import arcpy
arcpy.env.workspace="gis/main_map/main_map.gdb"
arcpy.env.overwriteOutput=True
import pandas as pd
import numpy as np

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