import numpy as np
import pandas as pd

from dicts import Links


buses_links=Links['buses_links']
rishui_dict=Links['rishui_dict']
service_type_dict=Links['service_type_dict']
time_periods=Links['time_periods']


def rishui_basic_data(lines_df):
    """ 
    function makes: basic rishui data of lines in flm
    function gets: dataframe of all buslines in israel and dataframe of relevant buses in jerusalem
    function returns: basic data for jlm lines
    """
    lines=pd.read_excel(buses_links['rishui_lines'])[[
        'מחוז','מקט','סוג קו',
        'כיוון', 'חלופה', 'שם סוג שירות', 'אורך מסלול',
        'ייחודיות הקו']].copy()
    
    lines.rename(columns = rishui_dict, inplace = True) 
    
    lines['makat']=lines['routeid'].astype(str)+'-'\
        +lines['direction'].astype(str)+'-'+lines['alternative'].astype(str) #makat
    #routeid_direction
    lines['routeid_direction']=lines['routeid'].astype(str)+'-'+lines['direction'].astype(str)
    lines['routeid']=lines['routeid'].astype(str)

     #east west
    lines['eastwest']=np.where(lines['eastwest']=='מזרח ירושלים', 1, 0)
    
    #take only lines in jlm lines_df
    lines_jlm = lines[lines['routeid'].isin(lines_df['routeid'])].copy()
    #service_type
    lines_jlm['type']=lines_jlm['line_type']+'-'+lines_jlm['service_type']
    #merge מהיר וישיר in inter-city service
    lines_jlm.loc[(lines_jlm['type']=='בינעירוני-מהיר')|
                  (lines_jlm['type']=='בינעירוני-ישיר'), 'type']='בינעירוני-מהיר'


    lines_jlm.replace({'type':service_type_dict}, inplace=True)
    print ('rishui data res12 is printed')
    return lines_jlm[['routeid','makat','routeid_direction', 'type', 'route_length', 'eastwest']]

###########################################################################################


def rishui_resolution3(rishui_res12):
    """ 
    function makes: rishui of resolution 3
    function gets: rishui of resolution 1/2
    function returns: rishui for routeid-direction
    """

    rishui_specific_columns=rishui_res12[['routeid_direction','eastwest','type', 'route_length', 'routeid'].copy()]
    rishui_lines_res3=rishui_specific_columns.groupby('routeid_direction', as_index=False).agg(
                                    {'eastwest':'first',
                                    'type':'first',
                                    'route_length':'mean',
                                    'routeid':'first'})
    print ('rishui data res3 is printed')
    return rishui_lines_res3

###########################################################################################


def rishui_resolutions(JLM_lines):
    """
    function makes: create rishui files in 3 resolutions by usin above functions      
    """
    risui_res12=rishui_basic_data(JLM_lines)
    rishui_res3=rishui_resolution3(risui_res12)
    return risui_res12, rishui_res3
###########################################################################################
###########################################################################################

def passengers_resolutions():
    """ 
    function makes: passengers number in each makat
    function gets:csv with validations in each stop in each routeid in Tuesday 10/01/2023
    function returns: 2 dataframes with number of passengers in each makat (res12) or routeid-direction (res3)
    """
    stops_olim=pd.read_excel(buses_links['NPTA_extractions'], sheet_name='validation_by_stationline') #import validation in stops by line data
    stops_olim['makat']=stops_olim['officelineid'].astype(str)+'-'\
    +stops_olim['direction'].astype(str)+'-'+stops_olim['linealternative'].astype(str) #makat
    #routeid_direction
    stops_olim['routeid_direction']=stops_olim['officelineid'].astype(str)+'-'+stops_olim['direction'].astype(str)
    passengers_res12=stops_olim.groupby('makat', as_index=False)['passengersnumber'].sum()
    passengers_res3=stops_olim.groupby('routeid_direction', as_index=False)['passengersnumber'].sum()

    passengers_res12['passengersnumber']=passengers_res12['passengersnumber']/1000
    passengers_res3['passengersnumber']=passengers_res3['passengersnumber']/1000

    print ('passengers numbers per line are printed')
    return passengers_res12, passengers_res3

###########################################################################################
###########################################################################################

def clean_ebitzua():
    """ 
    function makes: filters rishui bitzua trips to not intact trips by electronic control
    function gets: dataframe with rishui bitzua trips
    function returns: filtered trips
    """

     #take rishui bitzua report to 10/01/2023 from NPTA
    ebtzua=pd.read_excel(buses_links['NPTA_extractions'],sheet_name='bakara_elektronit', dtype={'trip_rb_time': 'str'})

    ebtzua['makat']=ebtzua['OfficeLineId'].astype(str)+'-'+\
        ebtzua['Direction'].astype(str)+'-'+ebtzua['LineAlternative'].astype(str)
    
    ebtzua['routeid_direction']=ebtzua['OfficeLineId'].astype(str)+'-'+\
        ebtzua['Direction'].astype(str)
    
    ebtzua['tripid_date']=ebtzua['TripId'].astype(str)+'-'+ebtzua['trip_date'].astype(str)

    #non intact trip - not described as intact (late/early/didn't happen/non-rishui trip)
    t='תקין' 
    ebtzua['not_intact'] = np.where(ebtzua['status_bakara_luz_nm']!=t, 1, 0)
    #Take only planned od planned and executed trips
    ebtzua=ebtzua[((ebtzua['trip_status_cd']=='r')|(ebtzua['trip_status_cd']=='rb'))]
    ebtzua['day_period'] = 1 #low_hour
    ebtzua.loc[ebtzua['trip_rb_time'].between(time_periods['morning_begin'],time_periods['noon_begin'],inclusive='left'), 'day_period'] = 2 #rush_hour
    ebtzua.loc[ebtzua['trip_rb_time'].between(time_periods['afternoon_begin'],time_periods['evening_begin'],inclusive='left'), 'day_period'] = 3 #rush_afternoon

    return ebtzua

###########################################################################################
###########################################################################################

def ebitzua_resolutions(): 
    """ 
    function makes: calculates number and pecent of non-intact trips to each routeid-direction-alternative-day period
    function gets: rishui-bizua datagrame for 10/01/2023, taken from NPTA 
    function returns: dataframe with number and percent of non intact trips by routeid-direction-alternative and day period
    """
    ebtzua=clean_ebitzua() # clean ebitzua for further analysis

    ebitzua_resolutinos=[]
    agg_dict={'res1':['makat','day_period'], 
            'res2':['makat'],
            'res3':['routeid_direction']}
    for res  in agg_dict.keys():
        ebtzua_grouped=ebtzua.groupby(agg_dict[res], as_index=False).agg(
            number_of_trips = ('tripid_date', 'nunique'),
            number_of_not_intact_trips = ('not_intact', 'sum'))

        ebtzua_grouped['not_intact_percent']=round(
            100*(ebtzua_grouped['number_of_not_intact_trips']/ebtzua_grouped['number_of_trips']),2)
        
        ebtzua_grouped.drop(['number_of_not_intact_trips', 'number_of_trips'], axis=1, inplace=True)
        ebitzua_resolutinos.append(ebtzua_grouped)

    print ('e-bitua data printed')
    return ebitzua_resolutinos[0], ebitzua_resolutinos[1], ebitzua_resolutinos[2]

