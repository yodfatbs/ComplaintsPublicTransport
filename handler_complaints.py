import pandas as pd
import numpy as np

def complatints_resolution1(relevant_complaints):
    """ 
    function makes: calculates number of reliability-related complaints to resolution 2: routeid-direction-alternative and day period
    function gets: filtered complaints
    function returns: dataframe with makat, day period and complaints
    """
    res1_complaints=relevant_complaints[relevant_complaints['hour'].notna()].copy()

    morning_begin = '06:00:00'
    noon_begin = '09:00:00'
    afternoon_begin = '15:00:00'
    evening_begin= '19:00:00'
    res1_complaints['day_period'] = 1 #low_hour
    res1_complaints.loc[res1_complaints['hour'].between(morning_begin,noon_begin,inclusive='left'), 'day_period'] = 2 #rush_morning
    res1_complaints.loc[res1_complaints['hour'].between(afternoon_begin,evening_begin,inclusive='left'), 'day_period'] = 3 #rush_afternoon

    #count number of complints by makat and day period
    complaints_num=res1_complaints.groupby(['makat','day_period'], as_index = False).agg(number_of_complaints=('Serial_number','nunique'))
    
    return complaints_num


###########################################################################################
###########################################################################################

def complatints_resolution2(relevant_complaints):
    """ 
    function makes: calculates number of reliability-related complaints to resolution 2: routeid-direction-alternative
    function gets: filtered complaints
    function returns: dataframe with makat, day period and complaints
    """

        #count number of complints by makat and day period
    complaints_num=relevant_complaints.groupby(['makat'], as_index = False).agg(
        number_of_complaints=('Serial_number','nunique'))


    #for logistic regression - if there are any complaints, put 1, else 0
    return complaints_num


###########################################################################################
###########################################################################################

def complatints_resolution3(relevant_complaints):
    """ 
    function makes: calculates number of reliability-related complaints to resolution 3: routeid-direction
    function gets: filtered complaints
    function returns: dataframe with makat, day period and complaints
    """

        #count number of complints by makat and day period
    complaints_num=relevant_complaints.groupby(['routeid_direction'], as_index = False).agg(
        number_of_complaints=('Serial_number','nunique'))
    #for logistic regression - if there are any complaints, put 1, else 0
    return complaints_num

###########################################################################################
###########################################################################################


def complaints_resolutions():
    complaints_file='external_files/transportation_ministry/complaints_clean.xlsx'
    complaint=pd.read_excel(complaints_file)
    relevant_complaints=complaint[complaint['relevant']==1].copy()
    res1=complatints_resolution1(relevant_complaints)
    res2=complatints_resolution2(relevant_complaints)
    res3=complatints_resolution3(relevant_complaints)

    print ('scomplaints data printed')

    return res1, res2, res3