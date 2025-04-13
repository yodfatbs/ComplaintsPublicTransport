###########################################################################################
###########################################################################################
def create_directness():
    directness=pd.read_csv('outputs/final_directness.csv')
    directness_res12=directness[['route_desc', 'directness']].copy()

    directness[['routeid','Direction','Alternative']] = directness['route_desc'].str.split('-',expand=True)
    directness['routeid_direction']=directness['routeid'].astype(str)+'-'+directness['Direction'].astype(str)
    directness_res3=directness.groupby('routeid_direction', as_index=False)['directness'].mean()
    return directness_res12, directness_res3

###########################################################################################
###########################################################################################

def create_res1(res1_dfs):
    res1=ebitzua_res1.merge(complaints_res1, on=['makat','day_period'])
    day_periods=res1['day_period'].drop_duplicates().to_frame()
    day_periods['tmp'] =1 

    res1_dfs=[risui_res12[['makat', 'type']],passengers_res12,directness_res12[['route_desc', 'directness']],service_areas_res12]
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
            output_res2=df
        else:
            output_res2=output_res2.merge(df, on ='makat')
    return output_res2.drop_duplicates()

###########################################################################################
###########################################################################################


def create_res3(res3_dfs):
    for i,df in enumerate(res3_dfs):
        if i==0:
            output_res3=df
        else:
            output_res3=output_res3.merge(df, on ='routeid_direction')
    return output_res3.drop_duplicates()

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
            'passengersnumber_thousands']
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
def merge_and_export():
    directness_res12, directness_res3=create_directness()

    res1_dfs=[risui_res12[['makat', 'type']],passengers_res12,directness_res12[['route_desc', 'directness']],service_areas_res12]


    res2_dfs=[risui_res12[['makat', 'type']],passengers_res12,ebitzua_res2,
            directness_res12[['route_desc', 'directness']],service_areas_res12, complaints_res2]

    res3_dfs=[risui_res3[['routeid_direction', 'type']],passengers_res3,ebitzua_res3,
                directness_res3,service_areas_res3, complaints_res3]

    outputr_res1=create_res1(res1_dfs)
    output_res2=create_res2(res2_dfs)
    output_res3=create_res3(res3_dfs)

    dfs=[outputr_res1,output_res2,output_res3]
    export_to_excel(dfs)


###########################################################################################
###########################################################################################