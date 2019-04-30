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
- install python 2.7 using a conda environment and necessary packages (check mnual for full list:https://github.com/mdelgadoblasco/snap2stamps/)
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
- install either ArcGIS, QGIS or Gdalfor post processing and merging of DEM tiles


## Downloading data

In part 1 the instructions for data downloading are given. You can use either alaska satellite facility or the copernicus hun for data downloading.
This instruction will be for the Alaska sattelite facility but for the copernicus hub you can use www......

Surf to www.alaskasattelite.....

- select the AOI (are of interest)
AOI for project is:
Lat min
Lat max
Lon min
Lon max
- select satellites
For moat of 2016 only Sentinel 1A data is available, after that also Sentinel 1B.
The 2 satellites combined will provide 1 image every 6 days.
- select data product.
For this project only SLC data will be used.
- select flight direction
Be sure to download ascending and descending data seperately since they cant be combined.
- if you want to download certain tiles seperately you can search based on path and frame aswell
- Use seasonal search to find data within a set ammount of years and months, almost all data used for the project is between first of june and last of october of 2016 and 2018. A full data list and downloader scripts can be requested at g.j.vanleeuwens@gmail.com.

After searching data that meets the requirements add all the data files to the download que.
In the download que window choose download python script and enter your earthdata login credentials.
Move the download python script to the folder where you want the data to be downloaded to.
Open a terminal in the directory the python download file is located.
Execute the command:
Location_python3.exe download-all-dates.py
Example:
C:/programdata/miniconda3/pyth_env/python.exe download-all-dates.py

All Data will now be downloaded and if already downloaded controlled for corruption and redownloaded or skipped.

## SNAP Preprocessing

In this part the preprocessing using snap2stamps and SNAP will be given.

To be able to use the snap2stamps package a working python2.7 installation is required including these packages:
- pathlib, .........

Before we can use snap2stamps the directory has to be set up.
Snap2stamps expects the data to be sorted in 2 seperate folders: master and slaves. In the master directory is the preprocessed master and the original data located. In the slaves folder are all other unprocessed slave images. NOT UNZIPPED!

STEP 1:
Open all images in SNAP desktop
Navigate to radar - interferometric - INSAR stack overview.
Open all data in the window and click overview this will tell you which image is ideal to use as a master.

Step 2:
Use radar - interferometric - tops - tops split on the master to select the necessary subswath and bursts.
Use radar - apply orbit file on the output of the last step (be sure to use precise orbits).

Step 3:
Open the config file located in the snap2stamps folder with a text editor.
Change all parameters accordingly to below example.
Note:
- the importance of the correct file structure
- the / after the paths or not
- the IW1= parameter needs for example IW2 - not 2!
- the complete path to the master!

Step 3:
Move the config file to the folder in snap2stamps with the python scripts and open a terminal in this location.

In terminal type:
Python27.exe slaves_prep.py file.config

For example:

C:/programdata/miniconda3/pyth_env/python.exe slaves_prep.py file.config

This script will put the slaves in the right file structure to be processed by SNAP

Step 4

After step 3 also execute the other 3 scripts in this order:
Slaves_split.py, ..............

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


