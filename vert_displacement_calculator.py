### script to calculate the vertical displacement from the LOS displacements from stamp

###         modules:
import numpy as np
import pandas as pd
import math

###         Parameters:
# just changing year will calculate everything for that year/
year = '2018\\'
year_clean ='2018'

#setup all folder extensions so the right things can be calculated
asc_folder = 'E:\\Thesis\\1_insar_data\\ascending\\90_222\\' + year
desc_folder1 ='E:\\Thesis\\1_insar_data\\descending\\25_365_366\\' + year
desc_folder2 = 'E:\\Thesis\\1_insar_data\\descending\\127_366_367_368\\' + year
folder_list = [asc_folder, desc_folder1, desc_folder2]
asc_angle = 33.0
desc1_angle = 38.7
desc2_angle = 43.4
angle_list = [asc_angle, desc1_angle, desc2_angle]
insar_masterdate_2016 = ['20160801\\', '20160716\\', '20160723\\']
insar_masterdate_2018 = ['20180803\\', '20180730\\', '20180725\\']
name_abrv_list = ['asc_90_222_' + year_clean, 'desc_25_365_' + year_clean, 'desc_127_366_' + year_clean]
if year == '2016\\':
  insar_masterdate = insar_masterdate_2016
elif year == '2018\\':
  insar_masterdate = insar_masterdate_2018

resolution = '30m'
file_name = 'stamps_tsexport_'+ resolution + '.csv'

###         Functions:

# read the csv export with the StaMPS data
def excel_reader(
        path, file_name):
    total_dir = path + file_name
    df = pd.read_csv(total_dir, sep=',', skiprows = 2 , header = None)
    return df

#retrieve just the coordinates and the LOS velocity from the csv
def velocity_getter(
        df):
    df_vel = df.iloc[:,0: 3]
    return df_vel

# calculate the vertical_displacement from the LOS displacement and write it to the 4th array
def displacement_calculator(
        df,incidence_angle):
    nrows,ncols = df.shape
    df_vert_vel = pd.DataFrame([], index = range(nrows), columns= range(ncols))
    print (df_vert_vel.shape)
    for col in range(ncols):
      if col == 0 or col == 1:
          df_vert_vel.iloc[:,col] = df.iloc[:,col]
      else:
          df_vert_vel.iloc[:,col]= (df.iloc[:,col]) /(np.cos(math.radians(incidence_angle)))
    return df_vert_vel


# export the data into a new csv consisting of 4 columns : coordinates los and vertical diplacement
def df_exporter(df, output_path):
    df.to_csv(output_path, index = False, header = True, sep=',' , decimal ='.')
    return


###         Pipeline:

for path,date,angle,name_abrv in zip(folder_list,insar_masterdate,angle_list, name_abrv_list):
    total_path = path + 'INSAR_' + date
    output_path = path + 'results\\vertical_disp_' + name_abrv + '.csv'

    df = excel_reader(total_path,file_name)
    # df_vel = velocity_getter(df)
    df_vert_vel = displacement_calculator(df, angle)
    df_exporter(df_vert_vel, output_path)
    df = None


###         options/TODO
# - change the out_file to the original csv with a new column at end being or the LOS-velocity getting vertical velocity.
# - create an ouput csv with other script from combined points to import into stamps_visualizer.