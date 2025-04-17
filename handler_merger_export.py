
def create_res1(res1_dfs,ebitzua_res1,complaints_res1):
    res1=ebitzua_res1.merge(complaints_res1, on=['makat','day_period'], how='left')
    day_periods=res1['day_period'].drop_duplicates().to_frame()
    day_periods['tmp'] =1 

    for i,df in enumerate(res1_dfs):
        if 'makat' not in df.columns:
            df.rename(columns={'route_desc':'makat'}, inplace=True)
        if i==0:
            output_res1=df
        else:
            output_res1=output_res1.merge(df, on ='makat')

    output_res1['tmp'] =1 
    ready_tomerge=output_res1.merge(day_periods, on='tmp', how='left')


    output_res1=ready_tomerge.merge(res1,on=['makat', 'day_period'], how='left')
    output_res1.drop(columns='tmp', inplace=True)
    return output_res1.drop_duplicates()

###########################################################################################
###########################################################################################


def create_res2(res2_dfs):
    for i,df in enumerate(res2_dfs):
        if 'makat' not in df.columns:
            df.rename(columns={'route_desc':'makat'}, inplace=True)
        if i==0:
            r2=df
        elif i==len(res2_dfs)-1:
            r2=r2.merge(df, on ='makat', how='left')
            r2['number_of_complaints'].fillna(0, inplace=True)
        else:
            r2=r2.merge(df, on ='makat', how='inner')

    return r2.drop_duplicates()

###########################################################################################
###########################################################################################


def create_res3(res3_dfs):
    for i,df in enumerate(res3_dfs):
        if i==0:
            r3=df
        elif i==len(res3_dfs)-1:
            r3=r3.merge(df, on ='routeid_direction', how='left')
            r3['number_of_complaints'].fillna(0, inplace=True)
        else:
            r3=r3.merge(df, on ='routeid_direction', how='inner')
    return r3.drop_duplicates()

###########################################################################################
###########################################################################################

def export_to_excel(dfs):
    for int, res in enumerate(dfs):
        int=int+1

        name_dict={'eastwest':'East_JLM_lines', 
            'type': 'service_types', 
            'passengersnumber':'passengersnumber_thousands',
        'directness':'Directness_measurements', 
        'settlements': 'Settlements_lines', 
        'west':'West_metropolin_lines', 
        'injlm':'InJerusalem_lines',
        'headway':'Lines_headway', 
        'not_intact_percent':'percent_problematic_trips'
    }
        res.rename(columns=name_dict, inplace=True)

        general_columns=['East_JLM_lines', 'service_types', 
            'Directness_measurements', 'Settlements_lines',
            'West_metropolin_lines', 'InJerusalem_lines',
            'percent_problematic_trips', 'number_of_complaints',
            'passengersnumber_thousands','socioeco_2019']
        if int==1:
            cols=['makat', 'day_period']
        elif int==2:
            cols=['makat']
        else:
            cols=['routeid_direction']
        
        export_columns=cols+general_columns

        res[export_columns].to_csv(f'outputs/res{int}.csv', index=False)
        print(f'res{int} exported')

###########################################################################################
###########################################################################################
def merge_and_export(res1_dfs, res2_dfs, res3_dfs,ebitzua_res1,complaints_res1):


    outputr_res1=create_res1(res1_dfs,ebitzua_res1,complaints_res1)
    outputr_res1.loc[outputr_res1['makat']=='13068-1-ז', #fix null values
                     ['percent_problematic_trips','number_of_complaints']] = 0,0
    
    output_res2=create_res2(res2_dfs)
    output_res3=create_res3(res3_dfs)

    dfs=[outputr_res1,output_res2,output_res3]
    export_to_excel(dfs)
    return outputr_res1, output_res2,output_res3


###########################################################################################
###########################################################################################