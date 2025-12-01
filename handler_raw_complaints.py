import numpy as np
import pandas as pd

def find_excluded_word(complaints_copy):
    """
    function gets: complaints df with text and subject
    function returns: column 'words to exclude' specefies wether there are irrelevant words in complaint
    """
    
    words_to_exclude=['ערעור','קנס', 'ערעורים', 'תעריף']
    complaints_copy['words_to_exclude']=1

    #if subject or text contains irrelevant word, mark
    complaints_copy.loc[~(complaints_copy['new_case_essence'].str.contains('|'.join(words_to_exclude), case=False,na=True))&
    ~(complaints_copy['subjectname'].str.contains('|'.join(words_to_exclude), case=False,na=True)), 'words_to_exclude'] = None

###########################################################################################
###########################################################################################
def find_included_words(complaints_copy):
    """
    function gets: complaints df with text and subject
    function returns: column 'words to include' specefies wether there are relevant words in complaint
    """

    words_to_include=['איחור','הקדמה','עצר','עצירה','דילג','ביצוע']
    complaints_copy['words_to_include']=None

    #word to include
    complaints_copy.loc[(complaints_copy['new_case_essence'].str.contains('|'.join(words_to_include), case=False,na=True))|
    (complaints_copy['subjectname'].str.contains('|'.join(words_to_include), case=False,na=True)), 'words_to_include']=1

###########################################################################################
###########################################################################################
def fine_line_number(complaints_copy):
    """
    function gets: complaints df with line details - officelineid,direction,alternative
    function returns: columns of makat(officelineid,direction,alternative) and routeid-direction(officelineid,direction)
    """

    #check for makat derails
    complaints_copy['makat']=complaints_copy['officelineid'].astype(str)+\
        '-'+complaints_copy['LineDirection'].astype(str)+'-'+complaints_copy['LineAlternative'].astype(str)
    complaints_copy['routeid_direction']=complaints_copy['officelineid'].astype(str)+\
        '-'+complaints_copy['LineDirection'].astype(str)
    
###########################################################################################
###########################################################################################
def find_relevant_complaints(complaints_copy):
    """
    function gets: complaints df with line details - officelineid,direction,alternative
    function returns: column stating if the complaint is relevant for further analysis
    """
    complaints_copy['relevant']=None

    find_included_words(complaints_copy)
    find_excluded_word(complaints_copy)
    fine_line_number(complaints_copy)

    complaints_copy.loc[(complaints_copy['words_to_include']==1)& #only complaints with relevant words
                        (complaints_copy['words_to_exclude']!=1)& #without irrelevant words
                        (complaints_copy['officelineid'] != -1),'relevant'] = 1 #with line number
###########################################################################################
###########################################################################################    
def reverse_reversed_hour(complaints_copy):
    # # reverse mistyped time (from 'MM:HH' to 'HH:MM')
    complaints_copy['hour']=np.where(
        (~complaints_copy['hour'].isna()) #existing value for hour
        &
        #1st two characters (12:xx) are between 25 and 60 (for minutes) 
        (pd.to_numeric(complaints_copy['hour'].str[:2], errors='coerce').astype('Int64').between(25, 60, inclusive='both'))
    &
    #last two characters (xx:12) lower than 24 (for hour)
    (pd.to_numeric(complaints_copy['hour'].str[-2:], errors='coerce').astype('Int64')<=24),
    #reverse order
    complaints_copy['hour'].str[-2:] +complaints_copy['hour'].str[2]\
        + complaints_copy['hour'].str[:2],complaints_copy['hour']) 
 ###########################################################################################
###########################################################################################   
def replace_24_in_00(complaints_copy):
    # # replace hour 24 to 00
    complaints_copy['hour']=np.where(
    (~complaints_copy['hour'].isna()) #existing value for hour
    &(pd.to_numeric(complaints_copy['hour'].str[:2], errors='coerce').astype('Int64')==24), # if 1st 2 characters are 24
    '00:'+complaints_copy['hour'].str[-2:],complaints_copy['hour']) #change it to 00:
    complaints_copy.loc[complaints_copy['hour']>'24:00', 'hour']=None #drop errors - hur larger than 24:00

###########################################################################################
###########################################################################################
def find_hours(complaints_copy):
    """
    function gets: complaints df with text
    function returns: column with incident number, if its exist in the text
    """

    pattern = r'(\d{2}:\d{2})' #pattern of hour for regex
    complaints_copy['hour']=complaints_copy['new_case_essence'].str.extract(pattern, flags=0, expand=True)

    # # reverse mistyped time (from 'MM:HH' to 'HH:MM')
    reverse_reversed_hour(complaints_copy) 

    # # replace hour 24 to 00
    replace_24_in_00(complaints_copy)
###########################################################################################
###########################################################################################

def create_basic_complaints():
    complaint_link="https://zenodo.org/record/17737309/files/complaints_raw_sample.xlsx?download=1" #dosn't show on git

    complaints_copy=pd.read_excel(complaint_link)
    find_hours(complaints_copy)
    find_relevant_complaints(complaints_copy)
    complaints_clean=complaints_copy[
        ['ticketnumber', 'subjectname', 'incident_date','makat',
      'routeid_direction','hour','words_to_include', 'words_to_exclude','relevant']]
    
    # complaints_clean.to_excel('external_files/transportation_ministry/complaints_clean.xlsx', index=False)
    return complaints_clean
