### script to combine the vertical displacements from asc and desc stamps output into a mean displacement raster

###         modules:
import numpy as np
import pandas as pd
from osgeo import gdal
import shapefile as shp
import csv
from osgeo import ogr
from osgeo import gdalconst
import urllib
from urllib.request import urlopen
import sys
import math
import osr

###         parameters:

# only the parameter year has to be changed when the file structure is correct, this will makke a mean file for all files from that year.
year = '2018'
displacement_or_standarddeviation = 'DISP' ## STD or DISP
implement_csv2shape_and_tiff = True

if displacement_or_standarddeviation == 'DISP':
    asc_folder = 'E:\\Thesis\\1_insar_data\\ascending\\90_222\\' + year +'\\results\\'
    desc_folder_1 ='E:\\Thesis\\1_insar_data\\descending\\25_365_366\\'+ year +'\\results\\'
    desc_folder_2 = 'E:\\Thesis\\1_insar_data\\descending\\127_366_367_368\\' + year +'\\results\\'
    csv_location_list = [asc_folder,desc_folder_1,desc_folder_2]
    asc_name = 'vertical_disp_asc_90_222_' + year
    desc_name1 = 'vertical_disp_desc_25_365_' + year
    desc_name2 = 'vertical_disp_desc_127_366_'  + year
    csv_name_list =[asc_name, desc_name1, desc_name2]
    out_path = 'E:\\Thesis\\1_insar_data\\results\\mean_vertical_displacement_' + year + '.tif'
    out_path_csv = 'E:\\Thesis\\1_insar_data\\results\\mean_vertical_displacement_' + year + '.csv'
elif displacement_or_standarddeviation =='STD' :
    asc_folder = 'E:\\Thesis\\1_insar_data\\ascending\\90_222\\' + year +'\\results\\'
    desc_folder1 = 'E:\\Thesis\\1_insar_data\\descending\\25_365_366\\' + year + '\\results\\'
    desc_folder2 = 'E:\\Thesis\\1_insar_data\\descending\\127_366_367_368\\' + year + '\\results\\'
    csv_location_list = [asc_folder, desc_folder1, desc_folder2]
    # insar_masterdate_2016 = ['20160801\\', '20160716\\', '20160723\\']
    # insar_masterdate_2018 = ['20180803\\', '20180730\\', '20180725\\']
    # csv_name_list = ['asc_90_222_' + year, 'desc_25_365_' + year, 'desc_127_366_' + year]
    asc_name = 'vertical_disp_asc_90_222_' + year + 'vs'
    desc_name1 = 'vertical_disp_desc_25_365_' + year + 'vs'
    desc_name2 = 'vertical_disp_desc_127_366_'  + year + 'vs'
    csv_name_list =[asc_name, desc_name1, desc_name2]
    # if year == '2016':
    #     insar_masterdate = insar_masterdate_2016
    # elif year == '2018':
    #     insar_masterdate = insar_masterdate_2018
    #
    # resolution = '30m'
    # file_name = 'stamps_tsexport_vs' + resolution
    out_path = 'E:\\Thesis\\1_insar_data\\results\\mean_vertical_displacement_STD' + year + '.tif'
    out_path_csv = 'E:\\Thesis\\1_insar_data\\results\\mean_vertical_displacement_STD' + year + '.csv'
    out_path_shp = 'E:\\Thesis\\1_insar_data\\results\\vertical_displacement_STD'

ex_tif = 'E:\\Thesis\\2_Optical_data\\DNBR_0726_0904_30m_UTM_22N.tif'  # any tif that is the baseline of how the output should look.
ex_tif_wgs = 'E:\\Thesis\\2_Optical_data\\DNBR_0726_0904_60m_wgs_84.tif'
data = gdal.Open(ex_tif_wgs)
targetSR = osr.SpatialReference()
targetSR.ImportFromWkt(data.GetProjectionRef())

###         functions:

# function that translates the csvs with LOS and Vertical displacements into a shapefile with the vertical disp as attribute.
def csv_to_shape(csv_path,shp_path,prj_path,targetSR):
    #Set up blank lists for data
    x,y,id_no,date,target=[],[],[],[],[]

    #read data from csv file and store in lists
    with open(csv_path, 'r') as csvfile:
        r = csv.reader(csvfile, delimiter=',')
        rows = sum(1 for row in csvfile)
        df= pd.read_csv(csv_path, delimiter = ',')
        rows,cols =df.shape
        # get number of columns
        print (rows)
        print (cols)
        csv_cols = [[] for x in range(cols)]
        for col in range(len(csv_cols)):
            for index, row in df.iterrows():
                if index > 0: #skip header
                    csv_cols[col].append(float(row[col]))

    #Set up shapefile writer and create empty fields
    w = shp.Writer(shp_path, shp.POINT)
    w.autoBalance = 1 #ensures gemoetry and attributes match

    w.field('X', 'F', 10,8)
    w.field('Y', 'F', 10, 8)
    w.field('velocity', 'F', 50)

# deze rijen ook aanbrengen in de w.record en dan doorsturen naar raster en de combinatie uiteindelijk.
#     for attribute in range((len(csv_cols) - 3)):
#         w.field(attribute, 'N', 50)

    #loop through the data and write the shapefile
    for j,k in enumerate(csv_cols[0]):
        w.point(k,csv_cols[1][j]) #write the geometry
        w.record(k, csv_cols[1][j],csv_cols[2][j])
        # for col in range(len(csv_cols)):
        #     if col >= 2:
        #         w.record(csv_cols[col][j]) #write the attributes

    #Save shapefile
    w.close()

    prj = open(prj_path, 'wt')
    # # epsg = getWKT_PRJ('4326')
    # dest_srs = ogr.osr.SpatialReference()
    # dest_srs.ImportFromEPSG(32622)
    wkt = targetSR.ExportToWkt()
    prj.write(wkt)
    prj.close()
    return


def getWKT_PRJ (epsg_code):
    wkt = urlopen('http://spatialreference.org/ref/epsg/{0}/prettywkt/'.format(epsg_code))
    # remove_spaces = wkt.read().replace(' ','')
    # output = remove_spaces.replace('\n', '')
    return wkt

# function to rasterize the shapefiles so we can calculate the mean over every pixel row in a later step.
def rasterizer(raster_output, shp_input, ex_tif):
    # get the datafiles
    ndsm = ex_tif
    shp = shp_input

    data = gdal.Open(ndsm, gdalconst.GA_ReadOnly)
    mb_v = ogr.Open(shp)

    targetSR = osr.SpatialReference()
    targetSR.ImportFromWkt(data.GetProjectionRef())

    #setup the metadata based on the example tif and the shapefile
    geo_transform = data.GetGeoTransform()
    source_layer = data.GetLayer()
    x_min = geo_transform[0]
    y_max = geo_transform[3]
    x_max = x_min + geo_transform[1] * data.RasterXSize
    y_min = y_max + geo_transform[5] * data.RasterYSize
    x_res = data.RasterXSize
    y_res = data.RasterYSize
    pixel_width = geo_transform[1]
    # nband = len(csv_cols)

    # sr= osr.SpatialReference()
    # sr.ImportFromEPSG(32622)
    # sr_wkt = sr.ExportToWkt()

    # create the empty raster for output
    target_ds = gdal.GetDriverByName('GTiff').Create(raster_output, x_res, y_res,1, gdal.GDT_Float32)
    target_ds.SetGeoTransform((x_min, pixel_width, 0, y_min, 0, pixel_width))
    target_ds.SetProjection(str(targetSR))

    # for band in range(nband):
    mb_l = mb_v.GetLayer()
    band = target_ds.GetRasterBand(1)
    NoData_value = -999
    band.SetNoDataValue(NoData_value)
    band.FlushCache()

    # burn the shapefile to the raster and save the output
    gdal.RasterizeLayer(target_ds, [1], mb_l, options =["ALL_TOUCHED=TRUE", "ATTRIBUTE=velocity"]) ## Attribute is name of field to rasterize ##options=["ATTRIBUTE=velocity"]

    target_ds.FlushCache()
    target_ds = None

# function for combining the asc and desc vertical displacements on the locations atleast 1 asc and desc value is available, no interpolation.
def asc_desc_combiner(raster_list):
    # read rasters as usable arrays
    asc_r = gdal.Open(raster_list[0]).ReadAsArray()
    desc1_r = gdal.Open(raster_list[1]).ReadAsArray()
    desc2_r = gdal.Open(raster_list[2]).ReadAsArray()

    # create empty output array
    nrows,ncols = asc_r.shape
    print (nrows,ncols)
    out_array = np.zeros((nrows,ncols))

    # loop through every pixel of the shape of 1 raster and calculate the nanmean if atleast 1 asc and desc value is available for a pixel, otherwise set pixel to nan
    for row in range(nrows):
        for col in range(ncols):
            pixel_list = [asc_r[row,col],desc1_r[row,col],desc2_r[row,col]]
            # if math.isnan(pixel_list[0]) == True:
            #     # print('asc_nan_pixel found, mean set to nan')
            #     pixel_mean = np.nan
            # elif math.isnan(pixel_list[1]) == True and math.isnan(pixel_list[2])== True:
            #     # print('desc double_nan_pixel found, mean set to nan')
            #     pixel_mean = np.nan
            # elif math.isnan(pixel_list[0]) == False and math.isnan(pixel_list[1]) == False and math.isnan(pixel_list[2])== False:
            #     pixel_mean = np.nanmean(np.array([pixel_list[0], np.nanmean(np.array([pixel_list[1], pixel_list[2]]))]))
            #     print (pixel_list[0])
            # elif math.isnan(pixel_list[0]) == False and math.isnan(pixel_list[1]) == True and math.isnan(pixel_list[2])== False:
            #     pixel_mean = np.nanmean(np.array([pixel_list[0], pixel_list[2]]))
            #     print(pixel_list[0])
            # elif math.isnan(pixel_list[0]) == False and math.isnan(pixel_list[1]) == False and math.isnan(pixel_list[2]) == True:
            #     pixel_mean = np.nanmean(np.array([pixel_list[0], pixel_list[1]]))
            #     print(pixel_list[0])
            # # write values of pixels to a complete array
            # out_array[row,col] = pixel_mean
            if (pixel_list[0]) == -999:
                # print('asc_nan_pixel found, mean set to nan')
                pixel_mean = -999
            elif (pixel_list[1]) == -999 and (pixel_list[2]) == -999:
                # print('desc double_nan_pixel found, mean set to nan')
                pixel_mean = -999
            elif (pixel_list[0]) != -999 and (pixel_list[1]) !=-999 and (pixel_list[2]) !=-999:
                pixel_mean = np.nanmean(np.array([pixel_list[0], np.nanmean(np.array([pixel_list[1], pixel_list[2]]))]))
                print (pixel_list[0])
            elif (pixel_list[0]) !=-999 and (pixel_list[1]) == -999 and (pixel_list[2])!= -999:
                pixel_mean = np.nanmean(np.array([pixel_list[0], pixel_list[2]]))
                print(pixel_list[0])
            elif (pixel_list[0]) !=-999 and (pixel_list[1]) !=-999 and (pixel_list[2]) == -999:
                pixel_mean = np.nanmean(np.array([pixel_list[0], pixel_list[1]]))
                print(pixel_list[0])
            # write values of pixels to a complete array
            out_array[row,col] = pixel_mean
    return out_array

# function to rasterize the output array created with the displacement values
def write_raster(ex_tif,out_path,outData):
    # load data
    ndsm = ex_tif
    data = gdal.Open(ndsm, gdalconst.GA_ReadOnly)

    targetSR = osr.SpatialReference()
    targetSR.ImportFromWkt(data.GetProjectionRef())

    # set metadata for output file
    geo_transform = data.GetGeoTransform()
    source_layer = data.GetLayer()
    x_min = geo_transform[0]
    y_max = geo_transform[3]
    x_max = x_min + geo_transform[1] * data.RasterXSize
    y_min = y_max + geo_transform[5] * data.RasterYSize
    x_res = data.RasterXSize
    y_res = data.RasterYSize
    pixel_width = geo_transform[1]

    #make the empty raster
    target_ds = gdal.GetDriverByName('GTiff').Create(out_path, x_res, y_res, 1, gdal.GDT_Float32)
    target_ds.SetGeoTransform((x_min, pixel_width, 0, y_min, 0, pixel_width))
    target_ds.SetProjection(str(targetSR))
    band = target_ds.GetRasterBand(1)
    NoData_value = -999
    band.SetNoDataValue(NoData_value)

    # write and flush data to disk
    band.WriteArray(outData, 0, 0)
    band.FlushCache()
    target_ds = None
    del outData

def raster_to_csv(InRaster,OutCSV):

    # open the raster and get some properties
    ds = gdal.OpenShared(InRaster, gdalconst.GA_ReadOnly)
    GeoTrans = ds.GetGeoTransform()
    ColRange = range(ds.RasterXSize)
    RowRange = range(ds.RasterYSize)
    rBand = ds.GetRasterBand(1)  # first band
    nData = rBand.GetNoDataValue()
    if nData == None:
        nData = np.nan  # set it to something if not set
    else:
        print("NoData value is {0}".format(nData))

    # specify the centre offset
    HalfX = GeoTrans[1] / 2
    HalfY = GeoTrans[5] / 2

    with open(OutCSV, 'w') as CSVwrite:
        for ThisRow in RowRange:
            RowData = rBand.ReadAsArray(0, ThisRow, ds.RasterXSize, 1)[0]
            for ThisCol in ColRange:
                if RowData[ThisCol] != nData:
                    if RowData[ThisCol] > -1000:
                        X = GeoTrans[0] + (ThisCol * GeoTrans[1])
                        Y = GeoTrans[3] + (ThisRow * GeoTrans[5])  # Y is negative so it's a minus
                        # this gives the upper left of the cell, offset by half a cell to get centre
                        X += HalfX
                        Y += HalfY
                        CSVwrite.write('{0},{1},{2}\n'.format(X, Y, RowData[
                            ThisCol]))  # I think newline might be different on linux

###         Pipeline:

# make a shapfile and raster for every csv with displacements (3 in this case)
raster_list = []

if displacement_or_standarddeviation == 'DISP':
    for location,csv_name in zip(csv_location_list, csv_name_list):
        if implement_csv2shape_and_tiff == True: ## do not remake shapefiles and rasters when just recreating the means.

            print ('creating shapefiles now.....')
            csv_path = location + csv_name + '.csv'
            print (csv_path)
            shp_path = location + csv_name + '.shp'
            print(shp_path)
            prj_path = location + csv_name + '.prj'
            csv_to_shape(csv_path,shp_path,prj_path,targetSR)
            print ('rasterizing now....')
            raster_path = location + csv_name + '.tiff'
            rasterizer(raster_path, shp_path, ex_tif)

        # create_raster_list
        raster_list.append(location + csv_name + '.tiff')
        print (raster_list[0])

    # calculate the combined displacements for ascending and descending and write it to a tif.
    mean_raster = asc_desc_combiner(raster_list)
    write_raster(ex_tif,out_path,mean_raster)

    ## make a shapefile from the combined asc and desc data
    raster_to_csv(out_path,out_path_csv)

elif displacement_or_standarddeviation == 'STD':
    # for location, masterdate, outabrv in zip(csv_location_list, insar_masterdate,csv_name_list):
    for location, csv_name in zip(csv_location_list, csv_name_list):
        if implement_csv2shape_and_tiff == True:  ## do not remake shapefiles and rasters when just recreating the means.

        #     print('creating shapefiles now.....')
        #     csv_path = location + 'INSAR_' + masterdate + file_name + '.csv'
        #     print(csv_path)
        #     shp_path = out_path_shp + outabrv + '.shp'
        #     print(shp_path)
        #     prj_path = out_path_shp + outabrv + '.prj'
        #     csv_to_shape(csv_path, shp_path, prj_path, targetSR)
        #     print('rasterizing now....')
        #     raster_path = out_path_shp + outabrv + '.tiff'
        #     rasterizer(raster_path, shp_path, ex_tif)
        #
        #     # create_raster_list
        # raster_list.append(out_path_shp + outabrv + '.tiff')
        # print(raster_list[0])

            print('creating shapefiles now.....')
            csv_path = location + csv_name + '.csv'
            print(csv_path)
            shp_path = location + csv_name + '.shp'
            print(shp_path)
            prj_path = location + csv_name + '.prj'
            csv_to_shape(csv_path, shp_path, prj_path, targetSR)
            print('rasterizing now....')
            raster_path = location + csv_name + '.tiff'
            rasterizer(raster_path, shp_path, ex_tif)

        # create_raster_list
        raster_list.append(location + csv_name + '.tiff')
        print(raster_list[0])

    # calculate the combined displacements for ascending and descending and write it to a tif.
    mean_raster = asc_desc_combiner(raster_list)
    write_raster(ex_tif, out_path, mean_raster)

    ## make a shapefile from the combined asc and desc data
    raster_to_csv(out_path, out_path_csv)

### possibilities:

# - make the same file but then for the standard deviation
# - interpolating before combining ascending and descending so we have more points
# - use a buffer round every point to combine ascending and descending
# - use kernel round raster to keep more data