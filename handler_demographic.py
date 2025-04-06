
from config_general import *


from dicts import demographic_dict,  demographic_columns, cbs_links
from general_functions import add_zeros_codoflocality, add_zeros_codofstatistical, turnzero


def urb():
    """
    read irganized urban demographic data of cbs    
    """
    socio_eco_urb_path= cbs_links['demographic_urb_path']
    #1. import as dataframe
    socio_eco_urb=pd.read_excel(socio_eco_urb_path, 
                                sheet_name='organized', 
                                dtype={'CODE OF LOCALITY': str,'CODE OF STATISTICAL AREA': str,'INDEX POPULATION 2019[1]':int})
    #2. create the complete stat area number
    socio_eco_urb['YISHUV_STAT11'] = socio_eco_urb['CODE OF LOCALITY'].apply(add_zeros_codoflocality)\
        +socio_eco_urb['CODE OF STATISTICAL AREA'].apply(add_zeros_codofstatistical)
    #3. get rid of unnecessary columns, and change columns names
    socio_eco_urb.rename(columns = demographic_dict, inplace = True) 
    socio_eco_urb=socio_eco_urb[socio_eco_urb.columns.intersection(demographic_columns)] #take only relevant columns
    return socio_eco_urb


def reg(search_type):
    """
    read organized demographic data of cbs, either 'sub' (suburbian) or 'reg' (regional)
    """
    if search_type=='sub':
        path = cbs_links['demographic_sub_path']
    elif search_type=='reg':
        path = cbs_links['demographic_reg_path']

    #1. import as dataframe
    socio_eco=pd.read_excel(path, sheet_name='organized', dtype={'CODE OF LOCALITY': str})
    socio_eco.dropna(subset='CODE OF LOCALITY', inplace=True)
    socio_eco['INDEX POPULATION 2019[1]'] = socio_eco['INDEX POPULATION 2019[1]'].fillna(0).astype(int)
    #2.create the complete stat area number
    socio_eco['YISHUV_STAT11'] = socio_eco['CODE OF LOCALITY']+"0001"

    #3.get rid of unnecessary columns, and change columns names
    socio_eco.rename(columns = demographic_dict, inplace = True) 
    socio_eco=socio_eco[socio_eco.columns.intersection(demographic_columns)]
    return socio_eco


def ultraorthodox():
    """
    read organized ultraorthodox percent by statistical area from
    """
#1.import as dataframe
    ultraorthodox_path=cbs_links['ultraorthodox_path']
    ultraorthodox=pd.read_excel(ultraorthodox_path, sheet_name='organized', dtype={'סמל יישוב': str,'אזור סטטיסטי':str})
    ultraorthodox.dropna(subset='סמל יישוב', inplace=True)
    #2.create the complete stat area number
    ultraorthodox['YISHUV_STAT11'] = np.where(ultraorthodox['אזור סטטיסטי']!='0',
    ultraorthodox['סמל יישוב'].apply(add_zeros_codoflocality)\
        +ultraorthodox['אזור סטטיסטי'].apply(add_zeros_codofstatistical),
                                                ultraorthodox['סמל יישוב']+"0001")
    #3.get rid of unnecessary columns, and change columns names
    ultraorthodox.rename(columns = {'חרדים: אחוזים':'ultraorthodox_percent'}, inplace = True) 
    ultraorthodox=ultraorthodox[ultraorthodox.columns.intersection(['YISHUV_STAT11','ultraorthodox_percent'])]
    return ultraorthodox
###########################################

def merge_demographic():
    """
    create and merge demographic data (ultraorthodox percent and socio economic rank) into one dataframe
    """
    #1. create all demographic dfs
    urban=urb()
    regional=reg('reg')
    suburbian=reg('sub')
    haredi=ultraorthodox()
#2. concat together based on statistic area
    socio_eco_urb_reg=pd.concat([urban, regional],ignore_index=True) #merge urban and regional
    #add suburbian that not already in
    rows_to_concatenate = suburbian[~suburbian['CODE OF LOCALITY'].isin(socio_eco_urb_reg['CODE OF LOCALITY'])]
    socio_eco_urb_surb_reg = pd.concat([socio_eco_urb_reg, rows_to_concatenate], ignore_index=True)
    demographic_table=pd.merge(socio_eco_urb_surb_reg, haredi, on='YISHUV_STAT11', how='left') #add haredi info
    demographic_table['updated_ultraorthodox_percent']=demographic_table['ultraorthodox_percent'].apply(turnzero).fillna(0) 

    # merge socio-economic and ultra orthodox together, export to csv
    demographic_table.to_csv("outputs/demographic_table.csv")
    return demographic_table
###########################################
###########################################
