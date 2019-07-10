# SNAP-StaMPS workflow documentation
Documentation on the bachelor thesis: AN ASSESMENT OF SENTINEL-1 RADAR IMAGERY TIME-SERIES ANAYLIS FOR MONITORING SEASONAL SURFACE SUBSIDENCE DUE TO PERMAFROST DEGRADATION AFTER A TUNDRA FIRE.
InSAR Subsidence for post-fire seasonal Permafrost degredation based on the 2017 Greenland fire.

This Project is part of the Course AB_1096 of the Free University Amsterdam departement Earth and Climate. Based on Procesing of Sentinel-1 data of 2016 and 2018 the project tries to describe seasonal change in permafrost degradation caused by wildfire induced dynamics. The processing is done using ESA's SNAP [Veci etal., 2014] and the software StaMPS by the Universitoy of Leeds [Hooper et al., 2007]. 

## Getting Started:

Below instructions will get a copy of the software and data working on your machine to test and contribute to above project.

### Prerequisites:

The processing Chain is dependant on
- Linux (Debian based)
- SNAP 6.0 and up
- STAMPS 4.1b
- SnaPHU
- Snap2StamPS 
- Python 2.7 and Python 3.0 (conda)
- MatLab (list toolboxes)
- QGIS or ArcGIS

## Installing
Linux is required for all processing after Downloading the Data and preprocessing using Snap and Snap2StamPS, compiling with cygwin on windows has not been succesfull for almost all users.
for this project you can use a Debian linux distribution like Ubuntu 14.04

### Installing for preprocessing
Downloading and preprocessing:
- install Python 3.0 using a conda environment (reccomended packages for post-processing: pandas, numpy, Gdal, ogr, shapely)
```
conda create -n yourenvname python=3.0 
```
- Install python 2.7 using a conda environment and necessary packages (check manual for full list:https://github.com/mdelgadoblasco/snap2stamps/)
```
conda create -n yourenvname python=2.7 pathlib 
```

- Download the Snap2Stamps GIT from: https://github.com/mdelgadoblasco/snap2stamps/
- Instal SNAP (S1 and S2 toolbox) for your operating system from: http://step.esa.int/main/download/
- Install QGis, ArcGIS or Gdal in python 

### Installing for processing in stamps:

- Install debian based linux in a virtual machine or as a dual boot (check minimum system requirements)
basic steps are:
1. Create a bootable usb device with your linux_distro.iso file and a program like: rufus
2. Boot pc from usb by changing boot settings
3. Install linux on pc when booting from usb
4. Change boot settings back to base operating system
5. System will now boot from the installed linux_distro

All commands can be run in the basic terminal directory except for the make and make install.
- install standard libraries
```
sudo apt-get update
Sudo apt-get install make
Sudo apt-get install build-essential g++
Sudo apt-get install gawk
Sudo apt-get install tcsh
```

- Install stamps on linux
Download files from the git: https://github.com/dbekaert/StaMPS
Extract zip
```
Cd stamps4.1b/src
Make
Make install
```
- Install SnaPHU
```
Sudo apt-get install snaphu
```
- Install Triangle
```
sudo apt-get install Triangle
```
- Clone the TRAIN git package (may need extra package to use git clone command)
train will be used after step 8 of stamps processing and has dependencies(not always needed): BEAM for re-projection of satellite data; NCL when using weather model data from the US; GMT for auxiliary tropospheric correction methods
```
git clone https://github.com/dbekaert/TRAIN.git
```
- Install Matlab
This step requires a full matlab license
Download unix installer for Matlab from: https://nl.mathworks.com/downloads/
note: if the installer asks if you want to change path names to keep libraries from conflicting choose yes!

- Install SNAP (not necessary if preprocessing is not done on the linux machine)
Download Unix installer from: http://step.esa.int/main/download/

- Install more dependencies
```
Sudo apt-get install matlab-support
```
- Install either ArcGIS, QGIS or Gdal for post processing and merging of DEM tiles


## Downloading data

In this chapter we will discuss where to download Sentinel-1 data for the PS-InSAR processing. You can use either alaska satellite facility or the copernicus hub as platform to download the data but this instruction will be for the Alaska sattelite facility. for the copernicus hub you could use: https://forum.step.esa.int/t/python-data-downloader/14308

### Searching data

Surf to https://vertex.daac.asf.alaska.edu/#

- Select the AOI (are of interest)
AOI for project is:
LONMIN=-51.84
LATMIN=67.78
LONMAX=-51.35
LATMAX=67.91
- Select satellites
The Sentinel mission consists of 2 satellites: Sentinel-1A, launched on 3 April 2014, and Sentinel-1B launched on 25 April 2016.
The 2 satellites combined will provide 1 image every 6 days since they both have a 12 day repeat cycle. The imagery is available in ascending and descending orbit and should both be downloaded (but kept seperate) to compute the vertical displacement.
- Select data product.
For this project only IW-SLC data will be used, information about IW-SLC can be found here: https://sentinel.esa.int/web/sentinel/technical-guides/sentinel-1-sar/products-algorithms/level-1/single-look-complex/interferometric-wide-swath
- Select flight direction and path/frame
Be sure to download ascending and descending data seperately since they can not be combined during the interferometry phase.
if you want to download certain tiles seperately you can search based on path and frame aswell
- Use seasonal search to find data within a set ammount of years and months, almost all data used for the project is between first of june and last of october of 2016 and 2018. A full data list and downloader scripts can be requested at g.j.vanleeuwens@gmail.com.

### downloading
After searching data that meets the requirements add all the data files to the download que.
In the download que window choose download python script and enter your earthdata login credentials.
Move the download python script to the folder where you want the data to be downloaded to.
Open a terminal in the directory the python download file is located.
Execute the command:
```
Location_python3.exe download-all-dates.py
```
Example:
```
C:/programdata/miniconda3/pyth_env/python.exe download-all-dates.py
```

All Data will now be downloaded and if already downloaded controlled for corruption and redownloaded or skipped.

## SNAP Preprocessing

In this chapter the preprocessing using snap2stamps and SNAP will be covered. The Preprocessing can be done on both Windows and linux, this documentation is for use on a Windows machine.
Snap2stamps are python wrappers for using the S1tbx of SNAP for interferometric preprocessing.
To be able to use the snap2stamps package a working python 2.7 installation is required: check chapter installation

### Setup
Before we can use snap2stamps the directory has to be set up.
Snap2stamps expects the data to be sorted in 2 seperate folders: master and slaves. In the master directory the preprocessed master and original data for the master should be located. In the slaves folder all unprocessed and unzipped slave data files should be located

- Step 1 - Master selection:
Open all images in SNAP desktop
Navigate to radar - interferometric - INSAR stack overview.
Open all data in the window and click overview this will tell you which image is ideal to use as a master based on the temporal and baseline characteristics of the SLC products.

- Step 2 - Master preprocessing:
Use radar - interferometric - tops - tops split on the master to select the necessary subswath and bursts.
Use radar - apply orbit file on the output of the last step (be sure to use precise orbits).

- Step 3 - Setup project.conf file:
Open the config file located in the snap2stamps folder with a text editor.
Change all parameters accordingly to below example.
```
######### CONFIGURATION FILE ######
###################################
# PROJECT DEFINITION
PROJECTFOLDER=E:\Thesis\1_insar_data\descending\127_366_367_368\2018\
GRAPHSFOLDER=C:\mdelgadoblasco-snap2stamps-c2362a6\graphs\
##################################
# PROCESSING PARAMETERS
IW1=IW3
MASTER=E:\Thesis\1_insar_data\descending\127_366_367_368\2018\master\S1A_IW_SLC__1SDH_20180725T095228_20180725T095255_022949_027D8C_FE0F_split_Orb.dim
##################################
# AOI BBOX DEFINITION
LONMIN=-51.84
LATMIN=67.78
LONMAX=-51.35
LATMAX=67.91
##################################
# SNAP GPT 
GPTBIN_PATH=C:/Program Files/snap/bin/gpt
##################################
# COMPUTING RESOURCES TO EMPLOY
CPU=8
CACHE=10G
##################################
```
Note:
The importance of the correct file structure
The / after the paths or not
The IW1= parameter needs for example IW2 - not 2!
The complete path to the master.dim!

- Step 4 - Execution Snap2StaMPS scripts:

Move the config file(can have every name you want) to the Snap2stamps/bin folder and open a terminal in this location(tympe cmd in search bar).

In terminal type:
```
complete_path_to/Python27.exe slaves_prep.py project.conf
```
For example:
```
C:/programdata/miniconda3/pyth_env/python.exe slaves_prep.py file.config
```
This script will put the slaves in the right file structure to be processed by SNAP

After step 4 also execute the other 3 scripts in this order:
splitting_slaves.py, coreg_ifg_topsar.py, stamps_export.py

- Notes:
The python wrappers of snap2stamps execute the graphs located in the snap2stamps/graphs folder, these graphs can be altered by any user. For example: 

To use an External Dem change all the mentions of DEMname (for example ASTRM) into External dem like this:
```
<demName>External DEM</demName>
```
and change the path to the external dem to the path where the dem (in GeoTiff and wgs84 unprojected) is located. like this:
```
<externalDEMFile>E:\Thesis\TAN_DEM\TAN_DEM_merged.tif</externalDEMFile>
```

Another option could be changing the estimate coherence from False to True like this:
```
<includeCoherence>True</includeCoherence>
```
Or oversampling the signal by changing the coregistration parameters like this:
```
<cohWinAz>5</cohWinAz>

<cohWinRg>20</cohWinRg>
```
## StaMPS processing

StaMPS is a software package developed for linux bash and the linux matlab environment, in order to complete all the steps we need todo both the preperation step in the terminal as the processing steps in matlab.

### pre-matlab processing
To start matlab processing we first have to setup an environment using the config.bash file that is delivered with the STaMPS installation.
Navigate to your StaMPS folder and open the config.bash file in a text editor, file is located here:
```
/home/username/your_proj_folder/StaMPS-4.1-beta/StaMPS_CONFIG.bash
```
Change all paths in this file to the correct paths to the software bin, if you can't find a path use the whereis command to locate the install directories like this:
```
whereis SNAPHU Triangle
```
change the paths in the file like this:
```
# set environment variables:
export STAMPS="/home/username/StaMPS"
export SNAP2STAMPS="/home/username/snap2stamps"
...
#if triangle and snaphu are not installed through the repositories (i.e. compiled locally):
export TRIANGLE_BIN="/home/username/software/triangle/bin"
export SNAPHU_BIN="/home/username/software/snaphu/bin"
...
export MATLABPATH=$STAMPS/matlab:`echo $MATLABPATH`
...
# use points not commas for decimals, and give dates in US english
export LC_NUMERIC="en_US.UTF-8"
export LC_TIME="en_US.UTF-8"
...
export PATH=${PATH}:$STAMPS/bin:$MATLABPATH:$SNAP2STAMPS/bin
```
And then upon opening the terminal add all paths to your ENV by sourcing the config file:
```
source /home/username/your_proj_folder/StaMPS-4.1-beta/StaMPS_CONFIG.bash
```

If you intend to use the TRAIN toolbox for atmoshperic correction aswelll you will have to source that config file aswell.
Navigate to your TRAIN folder, open the file in a text editor.
```
/home/username/TRAIN/config...
```
Edit the file like this:
```
```
And source the file in the same terminal as StAMPS
```
source 
```


Upon having setup the environment we can start processing, remember to source the config.bash file everytime a new terminal for processing is opened.
Open the folder with the stamps_export data:
```
cd /media/user/external_harddrive_/proj_folder/flight_direction/data/INSAR_masterdate_folder/
```
Then do the first processing step using this command:
```
mt_prep_snap MASTERDATE Full_path_to/INSAR_masterdate_folder/ Da Patch_azi Patch_range Patch_merge_x Patch_merge_y
```
for example:
```
mt_prep_snap 20160728 media/Gijs/Samsung_t5/Thesis/Ascending/90_222/2016/INSAR_20160728/ 0.4 3 2 50 200
```
This will start mt_prep_Snap with an amplitude dispersion treshold of 0.4 (between 0.4 and 0.42 is normal with 0.4 having less PS), 6 patches of 3 in azimuth and 2 in range and the patches overlap with 50 and 200m each.
If processing in 1 patch is possible without memory issues this is recommended.

Carefully read to the log of mt_prep_snap upon finishing and look whether the mean_amplitude is never 0 and there are not to much ps points without amplitude, this will throw errors later in stamps processing.
When done reading dont close the terminal but type:
```
matlab
```
This will open a matlab window in the right directory to do the further StaMPS processing.

### Matlab-Processing
In the opened matlab window all further processing will be done, by simply typing``` stamps(1,8)```all steps of Stamps will be executed.
Processing with all steps seperate may be better for parameterization though, in order to run 1 step or a certain ammount of steps type:
```
stamps(begin_step,end_step)
```
for step 2:
```
stamps(2,2)
```
for step 3 and 4:
```
stamps(3,4)
```

Except for running the program with default parameters we would like to be able to change parameter values.
To get all parameters and their values and then change them:
```
getparm
setparm('parameter_name', value)
```
Another usefull command is the information about interferograms and their temporal and baseline decorrelation
```
ps_info
```

- Step 1 load data

Converts the data into the formats required for PS processing and stores them in matlab workspaces.
This step has no important parameters to change

- Step 2 Estimate phase noise

Step 2 estimates the phase noise for every pixel in the interferograms via an iterative step.
There are alot of parameters controlling this step but barely any documentation on how to use them correctly for noise reduction. Some sources note that changing the ```filter_grid_size , clap_alpha and gamma_max_iterations``` could make the filtering stronger and reduce the overall noise.

- Step 3 PS selection

By buffering and using threshold values this step decides on letting PS with random phase fall out of the total PS.
By lowering the possible density of these random phase pixels using the ``` density/percent_rand``` parameter less noisy pixels will be kept.

- Step 4 PS Weeding

at step 4 other bad PS pixels(too much noise or ground contributions) will be weeded from the PS pixels left from step 3. The parameters are easy to grasp so some adjustements can be easily made here.
Reducing the weed_Standard_dev can easily remove the worse pixels from the group, any value between 0.65 and 1 is quite realistic.

- Step 5 merge and resampling

If you have chosen to process in multiple patches from mt_prep_snap the patches will be merged here for step 6. It is also an option to resample the PS points to a lower resolution for noise reduction. Keep in mind that making ```merge_resample_size ``` higher can lead to undersampling of the deformation that is being detected so should be used carefully.

- Step 6 SNAPHU phase unwrapping

Phase unwrapping creates the displacement values for the final results based on a stochastic process over all interferograms.
Step 6 is really important and prone to error so reprocessing this step multiple times is necessary to get good results.
The important parameters for step 6 are:

``` unwrap_prefilter_flag``` The recommendation for this parameter is to keep it on 'y' because this will extract the errors calculated at step 7 and adds them in after unwrapping to improve the accuracy of the unwrapping. If you want to process 1 run without the pre_filter you can use ```scla_reset``` to clear the values from step 7.

```unwrap_grid_size``` This parameter determines to what grid the PS pixels will be resampled for the unwrapping. Higher values will reduce noise from unwrapping but also can undersample your deformation, use this parameter for noise reduction but with caution.

```unwrap_gold_n_win``` , ```unwrap_time_win ``` and ``` unwrap_gold_alpha``` these parameters control the Goldstein filter that is used on the grid before unwrapping takes place and reduces noise on the fringes. Highering the alpha value will generally set the filter to filter more and can therefore undersample your deformation, the window and time size of the filter should be played with to obtain a good result. ```unwrap_gold_n_win``` can cause problems when not enough pixels fall inside of the window, it has to be highered than.

```drop_ifg_index``` This parameter makes sure the interferograms listed (by number as shown in ```ps_info```) are not used in the processing, if a interferogram is added the processing has to be rerun from step 3. Use this parameter if after multiple times this interferogram can still not be reliabely unwrapped.

- Step 7 Estimate spatially-correlated look angle error

Spatially-uncorrelated look angle (SULA) error was calculated in Step 3 and removed in Step 5.  InStep 7,  spatially-correlated look angle (SCLA) error is calculated which is due almost exclusivelyto  spatially-correlated  DEM  error  (this  includes  error  in  the  DEM  itself,  and  incorrect  mapping  ofthe DEM into radar co-ordinates).   Master atmosphere and orbit error (AOE) phase is estimated simultaneously.

The errors calculated in step 7 are importtant to improve the unwrapping results so the final result reaches its optimum state.

The most important parameters for step 7 are ```scla_drop_index``` and ```scla_deramp```. If a result is not reliabely unwrapped and you do not want to impact it the result of step 7 you can add the interferogram (number in ps_info) to the ```scla_drop_index``` and step 7 will skip this interferogram when calculating. Using ```scla_deramp``` may improve your results when high phase ramps are distorting your results, by setting parameter to 'y' it will calculate an extra error to be removed.

- Step 8 Atmospheric calculation using StaMPS

step 8 filters the results specifically for atmospheric disturbance, play with the parameters ```scn_wavelength``` and ```scn_time_win``` to see what works for your AOI.

### how to process in StaMPS

- run steps 1-6
- check ps_plot ('u')
- add bad ifgs to scla_drop_index
- run step 7
- check ps_plot('u-dm') is generally smoother
- rerun step 6
- check ps_plot('u') 
- remove ifgs that have improved in unwrapping result from scla_index and rerun step 7
- rerun step 6 and check again.

keep doing this process until results are satisfying and command:
```ps_plot('v-do'. 'ts')```
to check if the total velocities are okay, if result is not satisfying try:

- rerun from step 6 with more goldstein filtering
- rerun from step 5 with a higher ``` merge_resample_size``` 
- rerun from step 4 with changes to the ``` weed_standard_dev```  parameter
- rerun from step 2 with bad ifgs added to ``` drop_ifg_index```  and possible changes to parameters step 2 and 3

set your reference location for plotting using: 
``` 
setparm('ref_centre_lonlat' , [lon lat])
setparm('ref_radius', radius_m)
``` 

if all results are satisfying make a kml file with all data for visualization:
``` 
% save PS velocity estimation to a mat file
>> ps_plot('v-d', -1)
% load matfile
>> load ps_plot_v-d
% save ps.kml (generated from ph_disp for every 10 points with an opacity of 0.4
>> ps_gescatter('ps.kml',ph_disp,10,0.4)
``` 

or make a csv file with all data vor visualizations:
``` 
ps_plot('v-do', 'ts');
% after the plot has appeared magically, set radius and location by clicking into the plot
load parms.mat;
ps_plot('v-do', -1);
load ps_plot_v-do.mat;
lon2_str = cellstr(num2str(lon2));
lat2_str = cellstr(num2str(lat2));
lonlat2_str = strcat(lon2_str, lat2_str);

lonlat_str = strcat(cellstr(num2str(lonlat(:,1))), cellstr(num2str(lonlat(:,2))));
ind = ismember(lonlat_str, lonlat2_str);

disp = ph_disp(ind);
disp_ts = ph_mm(ind,:);
export_res = [lon2 lat2 disp disp_ts];

metarow = [ref_centre_lonlat NaN transpose(day)-1];
k = 0;
export_res = [export_res(1:k,:); metarow; export_res(k+1:end,:)];
export_res = table(export_res);
writetable(export_res,'stamps_tsexport.csv')
``` 

if you want to use TRAIN check the train manual: http://davidbekaert.com/download/TRAIN_manual.pdf
but using linear correction try this:
``` 
aps_linear
ps_plot('v-dao' , 'a_linear' , 'ts')
``` 

# post-StaMPS processing

To convert the corrected LOS displacements from stamps in to combined asc and des vertical displacement I have created a few python scripts to ease this process.
The scripts can be downloaded from this git and can be adjusted to your folder system.

# visualization

Visualization of the data in this project is done using QGIS and Python. All scripts used can be found in this Git and shapefiles used can be requested by contacting me directly. Scripts will have to be adjusted to personal file structure and projections to be usable.

## Authors

* **Gijs van Leeuwen** - *Processer and main author* - [https://github.com/gjvanleeuwen/]


## Acknowledgments
* **dr. Sander Veraverbeke** - *supervisor environmental processing and writing* [https://sites.google.com/view/sanderveraverbeke/sander-veraverbeke?authuser=0]
* **dr. Kanayim Teshebaeva** - *supervisor for InSAR processing* - 
* **STEP Forum contributors** - *software help and understanding*


