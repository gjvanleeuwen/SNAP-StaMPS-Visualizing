# ps_insar_snap-stamps
documentation on the publication of post-fire seasonal permafrost degradation in relation with InSAR subsidence.
InSAR Subsidence for post-fire seasonal Permafrost degredation.
- based on the 2017 Greenland fire

This Project is part of the Course AB_..... of the Free University Amsterdam departement Earth and Climate. Based on Procesing of Sentinel-1 data of 2016 and 2018 the project tries to describe seasonal change in permafrost degradation caused by wildfire induced dynamics. The processing is done using ESA's SNAP [Reference] and the software StamPS by the Universitoy of Leeds [reference]. 



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

### Installing


Linux is required for all processing after Downloading the Data and preprocessing using Snap and Snap2StamPS, compiling with cygwin on windows has not been succesfull for almost all users.
for this project you can use a Debian linux distribution like Ubuntu 14.04

# installing for preprocessing
downloading and preprocessing:
- install Python 3.0 using a conda environment
```
conda create -n yourenvname python=3.0 
```
- install python 2.7 using a conda environment and necessary packages (check manual for full list:https://github.com/mdelgadoblasco/snap2stamps/)
```
conda create -n yourenvname python=2.7 pathlib 
```

- download the Snap2Stamps GIT from: https://github.com/mdelgadoblasco/snap2stamps/
- instal SNAP (S1 and S2 toolbox) for your operating system from: http://step.esa.int/main/download/
- install QGis, ArcGIS or Gdal in python 

# Installing for processing in stamps:

- install debian based linux in a virtual machine or as a dual boot (check minimum system requirements)
basic steps are:
1. create a bootable nusb device with your linux_distro.iso file and a program like: rufus
2. boot pc from usb by changing boot settings
3. install linux on pc when booting from usb
4. change boot settings back to base operating system
5. system will now boot from the installed linux_distro

All commands can be run in the basic terminal directory except for the make and make install.
- install standard libraries
```
sudo apt-get update
Sudo apt-get install make
Sudo apt-get install build-essential g++
Sudo apt-get install gawk
Sudo apt-get install tcsh
```

- install stamps on linux
download files from the git: https://github.com/dbekaert/StaMPS
Extract zip
```
Cd stamps4.1b/src
Make
Make install
```
- install SnaPHU
```
Sudo apt-get install snaphu
```
- install Triangle
```
sudo apt-get install Triangle
```
- clone the train git package (may need extra package to use git clone command)
train will be used in step 8 of stamps processing and has dependencies: BEAM for re-projection of satellite data; NCL when using weather model data from the US; GMT for auxiliary tropospheric correction methods
```
git clone https://github.com/dbekaert/TRAIN.git
```
- install Matlab
This step requires a full matlab license
Download unix installer for Matlab from: https://nl.mathworks.com/downloads/
note: if the installer asks if you want to change path names to keep libraries from conflicting choose yes!

- install SNAP (not necessary if preprocessing is not done on the linux machine)
Download Unix installer from: http://step.esa.int/main/download/

- Install more dependencies
```
Sudo apt-get install matlab-support
```
- install either ArcGIS, QGIS or Gdal for post processing and merging of DEM tiles


## Downloading data

in this chapter we will discuss where to download Sentinel-1 data for the PS-InSAR processing. You can use either alaska satellite facility or the copernicus hub as platform to download the data but this instruction will be for the Alaska sattelite facility. for the copernicus hub you could use: https://forum.step.esa.int/t/python-data-downloader/14308

# Searching data

Surf to https://vertex.daac.asf.alaska.edu/#

- select the AOI (are of interest)
AOI for project is:
LONMIN=-51.84
LATMIN=67.78
LONMAX=-51.35
LATMAX=67.91
- select satellites
The Sentinel mission consists of 2 satellites: Sentinel-1A, launched on 3 April 2014, and Sentinel-1B launched on 25 April 2016.
The 2 satellites combined will provide 1 image every 6 days since they both have a 12 day repeat cycle. The imagery is available in ascending and descending orbit and should both be downloaded (but kept seperate) to compute the vertical displacement.
- select data product.
For this project only IW-SLC data will be used, information about IW-SLC can be found here: https://sentinel.esa.int/web/sentinel/technical-guides/sentinel-1-sar/products-algorithms/level-1/single-look-complex/interferometric-wide-swath
- select flight direction and path/frame
Be sure to download ascending and descending data seperately since they can not be combined during the interferometry phase.
if you want to download certain tiles seperately you can search based on path and frame aswell
- Use seasonal search to find data within a set ammount of years and months, almost all data used for the project is between first of june and last of october of 2016 and 2018. A full data list and downloader scripts can be requested at g.j.vanleeuwens@gmail.com.

# downloading
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

In chapter the preprocessing using snap2stamps and SNAP will be covered. The Preprocessing can be done on both Windows and linux, this documentation is for use on a Windows machine.
Snap2stamps are python wrappers for using the S1tbx of SNAP for interferometric preprocessing.
To be able to use the snap2stamps package a working python 2.7 installation is required: check chapter installation

- setup
Before we can use snap2stamps the directory has to be set up.
Snap2stamps expects the data to be sorted in 2 seperate folders: master and slaves. In the master directory the preprocessed master and original data for the master should be located. In the slaves folder all unprocessed and unzipped slave data files should be located

- Step 1 - master selection:
Open all images in SNAP desktop
Navigate to radar - interferometric - INSAR stack overview.
Open all data in the window and click overview this will tell you which image is ideal to use as a master based on the temporal and baseline characteristics of the SLC products.

- Step 2 - master preprocessing:
Use radar - interferometric - tops - tops split on the master to select the necessary subswath and bursts.
Use radar - apply orbit file on the output of the last step (be sure to use precise orbits).

- Step 3 - setup project.conf file:
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

- Step 4 - execution Snap2stamps:
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

## StaMPS processing

if you havent yet, fill in the config.bash script with below template......
then open a terminal and enter:

source config.bash..... ## this will add all required commands to your PATH variable and make the scripts executable
cd location_of_insar_masterdate_folder ## example: cd E:\project\INSAR_20160803\
mt_prep_snap MASTER_DATE MASTERDATE_FOLDER_LOCATION DA PATCH_azimuth PATCh_..... OVERLAP_... OVERLAP_..... ## example: 

when mt_prep_snap is done command:
matlab

the rest of the processing will be done in the just opened up matlab interface

all the Matlab steps can be done using the command stamps(1,8) but step for step processing may be prefferedusing stamps (1,1) for step 1 and stamps(3,4) for step 3 and 4 for example.
all parameter values and the defaults can be see using getparms and changed using ................
for aparameter list for this project email (g.j.vanleeuwens@gmail.com), for exploration look at (blog part 2 gitlab)

all processing except for step 6-8 will be done by the patches, then at step 6 all patches will be combined.
keep in mind that SNAPHU Phase unwrapping has a stochastic factor because it has random starting points, run this process multiple times for good results!



## post-StaMPS processing

visualizing the StamPS output can be done using multiple ways: you can use the ps_plot functions, the google earth kml file generation, a wonderful QGIS plugin or as we did in this project the StamPS-Visualizer by:.....

to create the csv out putfor this plugin based on R and Rstudio follow this process:

code for vialize creation.

## visualization


## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc


