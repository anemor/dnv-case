import pandas as pd
import matplotlib.pyplot as plt
import dask.dataframe as dd
import geopandas as gpd

coastline = gpd.read_file("Norway_coast_cropped.shp")#.to_crs('EPSG:4326') #laste inn norge
#                     norway.buffer(0.25)).iloc[0].geometry
coast_gdf = gpd.read_file("Norway_coast_cropped.shp")#.to_crs('EPSG:4326')
coast_gdf = coast_gdf.clip_by_rect(xmin=10.43, ymin=59.37, xmax=10.7, ymax=59.46)
coast_gdf.plot()


#mmsi,    imo_num, date_time_utc           ,lat,   lon,sog,cog,true_heading,avgDraught,Grid_10_Id,Grid_1_Id,CourseDifference,SailedNMDistance,SailedSpeed,VesselLength,VesselDepth,ENV_Norwegian_Main_Vessel_Category_ID,RISK_Norwegian_Main_Vessel_Category_ID,GT_NorwegianMainVesselCategory_Id,Fuel_Type_Main_ID,Fuel_Type_Secondary_ID,Ship_cargo_type_ID,Hazmat_un_Id,vessel_length_group_id,Candidate_pg_closetoshore,Candidate_pg_criticalturn_starts,pg_critical_turn_distance_to_land,pg_ct_grounding_point_lon,pg_ct_grounding_point_lat,pg_ct_grounding_Grid_1_Id,pg_ct_grounding_Grid_10_Id,Candidate_coll_head,Candidate_coll_over,Candidate_coll_cross,Powered_grounding_type1,Powered_grounding_type2,dg_DriftDirection,dg_DriftDistance_NM,dg_TimeToImpact_Hour,dg_NoRecoveryProbability,dg_grounding_point_lon,dg_grounding_point_lat,dg_grounding_Grid_10_Id,dg_grounding_Grid_1_Id,cp_Collision_Headon,cp_Collision_overtaking,cp_Collision_crossing
#257846800,9771432,2022-08-04T17:46:53.000Z,59.4121,10.4908,0.9,269.6,269,4.0,25000_-3375000,28500_-3372500,"","","",142.900,5.000000000,9,16,3,1,1,"",0,6,0,0,"","","","","","","","",3.09542578348292E-7,7.79653032323063E-6,"","","","",0.0,0.0,"","",0.0,1.28766254360926E-5,8.37491932056106E-6

#mmsi,    Candidate_pg_closetoshore,   Candidate_pg_criticalturn_starts,   ,Candidate_coll_head,Candidate_coll_over,Candidate_coll_cross,    Powered_grounding_type1,Powered_grounding_type2   
# cp_Collision_Headon,cp_Collision_overtaking,cp_Collision_crossing
dtype_fix={'imo_num': 'float64',
           'pg_ct_grounding_Grid_10_Id': 'object',
           'pg_ct_grounding_Grid_1_Id': 'object'}
print('Loading CSV...')
df = dd.read_csv("candidates_202208.csv", dtype = dtype_fix, parse_dates=['date_time_utc'])[[ #laste inn candidates
                                                                          'mmsi',
                                                                          'date_time_utc',
                                                                          'lat',
                                                                          'lon',
                                                                          'sog',
                                                                          'true_heading',
                                                                          'Candidate_pg_closetoshore',   
                                                                          'Candidate_pg_criticalturn_starts',
                                                                          'Candidate_coll_head', #head on collision
                                                                          'Candidate_coll_over', #overtake collision
                                                                          'Candidate_coll_cross' #crossing collision
                                                                          ]]

dtype={'imo_num': 'float64',
       'pg_ct_grounding_Grid_10_Id': 'object',
       'pg_ct_grounding_Grid_1_Id': 'object'}

FERGE = ['BASTOE I', 
         'BASTO II',
         'BASTO IV',
         'BASTO V', 
         'BASTO VI',
         'BASTO ELECTRIC', 
         'VEDEROY']

FERGE_MMSI = [259401000, # 'BASTOE I',
              259402000, # 'BASTO II',
              257845600, # 'BASTO IV',
              257846800, # 'BASTO V', 
              257847600, # 'BASTO VI',
              257122880, # 'BASTO ELECTRIC', 
              259674000  # 'VEDEROY'
              ]

print('Filtering DataFrame...')
df = df.loc[df['mmsi'].isin(FERGE_MMSI)]

START_DATE = pd.Timestamp("2022-08-01", tz="UTC")
END_DATE = pd.Timestamp("2022-08-2", tz="UTC")
mask = (df["date_time_utc"] > START_DATE) & (df["date_time_utc"] < END_DATE)
df = df.loc[mask]
df = df.loc[df["sog"] >= 4]
df = df.set_index('date_time_utc')
# df = df.resample('30S').mean()

f = open("AISyRISK_morten_moss_analyse_all_2022_08.txt", "w")


print('Starting plotting')
for i,v in enumerate(FERGE_MMSI): #plot stuff
    #print(i,v)
    boat_df = df.loc[df['mmsi'] == v].compute()
    #print(boat_df.head)
    plt.plot(boat_df.lon, boat_df.lat, c='grey', label='BASTO IV path', linewidth=1, alpha=0.3)
    plt.scatter(boat_df.lon, boat_df.lat, c='grey', label='BASTO IV path', s=1, alpha=0.1)
    
    turn_df = boat_df.loc[boat_df['Candidate_pg_criticalturn_starts'] == 1]
    plt.scatter(turn_df.lon, turn_df.lat, c='red', label='head on', s=3)
    
    close_df = boat_df.loc[boat_df['Candidate_pg_closetoshore'] == 1]
    plt.scatter(close_df.lon, close_df.lat, c='cyan', label='crossing', s=3)
    
    head_df = boat_df.loc[boat_df['Candidate_coll_head'] == 1]
    plt.scatter(head_df.lon, head_df.lat, c='green', label='head on', s=3)
    
    over_df = boat_df.loc[boat_df['Candidate_coll_cross'] == 1]
    plt.scatter(over_df.lon, over_df.lat, c='yellow', label='crossing', s=3)
    
    cross_df = boat_df.loc[boat_df['Candidate_coll_cross'] == 1]
    plt.scatter(cross_df.lon, cross_df.lat, c='magenta', label='crossing', s=3)
    
    total_data_points = len(boat_df.index)
    critical_turn_candidates = boat_df['Candidate_pg_criticalturn_starts'].sum()
    close_to_shore_candidates = boat_df['Candidate_pg_closetoshore'].sum()
    head_on_collision_candidates = boat_df['Candidate_coll_head'].sum()
    overtake_collision_candidates = boat_df['Candidate_coll_over'].sum()
    crossing_collision_candidates = boat_df['Candidate_coll_cross'].sum()

    big_print = f'''
    ================================
    {FERGE[i]}, MMSI nr {v}.
    - total data points {total_data_points}
    - critical turn candidates {critical_turn_candidates}
    - close to shore candidates {close_to_shore_candidates}
    - head on collision candidates {head_on_collision_candidates}
    - overtake collision candidates {overtake_collision_candidates}
    - crossing collision candidates {crossing_collision_candidates}
    '''
    f.write(big_print)
    print(big_print)

f.close()

plt.legend()
plt.show()