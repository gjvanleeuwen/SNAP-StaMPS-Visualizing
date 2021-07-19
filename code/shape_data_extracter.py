### function to extract data froma raster under a polygon


### imports

from osgeo import gdal
from osgeo import gdal_array
import ogr
import osr
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats



### functions


def rasterizer(feature_iteration,cols,rows,src_rast,src_lyr,shape_rast_outpath):
    ### transforms a training sample shapefile to a raster containing 1 of the samples as raster pixels and returns the feature locaion ###
    # every new pixel of a training sample overrides the file with the new pixel

    h = feature_iteration
                # Get extent of feat
    feat = src_lyr.GetFeature(h)
    geom = feat.GetGeometryRef()
    if (geom.GetGeometryName() == 'MULTIPOLYGON'):
        count = 0
        pointsX = []; pointsY = []
        for polygon in geom:
            geomInner = geom.GetGeometryRef(count)
            ring = geomInner.GetGeometryRef(0)
            numpoints = ring.GetPointCount()
            for p in range(numpoints):
                lon, lat, z = ring.GetPoint(p)
                pointsX.append(lon)
                pointsY.append(lat)
            count += 1
    elif (geom.GetGeometryName() == 'POLYGON'):
        ring = geom.GetGeometryRef(0)
        numpoints = ring.GetPointCount()
        pointsX = []; pointsY = []
        for p in range(numpoints):
            lon, lat, z = ring.GetPoint(p)
            pointsX.append(lon)
            pointsY.append(lat)

    xmin = min(pointsX)
    xmax = max(pointsX)
    ymin = min(pointsY)
    ymax = max(pointsY)
    maskvalue = 1
    # xres=(xmax-xmin)/float(cols)
    # yres=(ymax-ymin)/float(rows)
    #geotransform=(xmin,xres,0,ymax,0, -yres)

    transform = src_rast.GetGeoTransform()
    xOrigin = transform[0]
    yOrigin = transform[3]
    pixelWidth = transform[1]
    pixelHeight = abs(transform[5])

    geotransform=(xmin,pixelWidth,0,ymax,0, -pixelHeight)
    cols = int((xmax - xmin) /pixelWidth)+1
    rows = int((ymax - ymin) /pixelHeight)+1

    print (pixelWidth,pixelHeight)
    print (xmin,xOrigin)
    print (ymax, yOrigin)
    xoff = int((xmin - xOrigin)/pixelWidth)
    yoff = int((ymax- yOrigin)/pixelWidth)
    xcount = int((xmax - xmin)/pixelWidth)+1
    ycount = int((ymax - ymin)/pixelWidth)+1

    xcount = cols
    ycount = rows

    sourceSR = src_lyr.GetSpatialRef()
    targetSR = osr.SpatialReference()
    targetSR.ImportFromWkt(src_rast.GetProjectionRef())

    dst_ds = gdal.GetDriverByName('Gtiff').Create(shape_rast_outpath + '.tif', cols , rows , 1 ,gdal.GDT_Byte)
    dst_ds.SetGeoTransform(geotransform)
    dst_ds.SetProjection( str(targetSR) )
    dst_rb = dst_ds.GetRasterBand(1)
    #dst_rb.Fill(0) #initialise raster with zeros
    dst_rb.SetNoDataValue(np.nan)

    err = gdal.RasterizeLayer(dst_ds, [maskvalue], src_lyr)
    dst_ds.FlushCache()

    mask_arr=dst_ds.GetRasterBand(1).ReadAsArray()
    mask_arr = None
    return xoff, yoff, xcount, ycount

def extract_values(extract_file_path,shape_raster_path, ycount, xcount, xoff, yoff): ### use = _AHN2, _AHN2_aspect, _AHN2_slope, BODEM, GEO

    ### returns a AHN2 value per inserted training sample and puts it to a list, usable for all ancillary data ###
    img_ds = gdal.Open(extract_file_path)

    #converts valuerasters to complete array
    # img = np.zeros((ycount, xcount, 1),
    # gdal_array.GDALTypeCodeToNumericTypeCode(img_ds.GetRasterBand(1).DataType))
    # img[:, :, 0] =  np.flipud(img_ds.GetRasterBand(1).ReadAsArray(xoff, yoff, xcount, ycount))

    img = np.flipud(img_ds.GetRasterBand(1).ReadAsArray(xoff, yoff, xcount, ycount))

    roi_ds = gdal.Open(shape_raster_path + '.tif')
    #converts traingsample_raster to array
    roi = roi_ds.ReadAsArray(0, 0, xcount, ycount).astype(np.float)

    boolean = roi >= 100
    count = len(roi[boolean])

    extracted_values = np.array((img[boolean]) )#[:, :, 0]
    extracted_values = img[np.where(roi >=100)]
    mean = np.nanmean(extracted_values[np.where(extracted_values > -999)])

    return extracted_values , mean , boolean , img


### parameters:



###         pipeline

rasterpath_16 = r'E:\\Thesis\\1_insar_data\\results\\mean_vertical_displacement_2016.tif'
rasterpath_18 = r'E:\\Thesis\\1_insar_data\\results\\mean_vertical_displacement_2018.tif'
STD_rasterpath_16 = r'E:\\Thesis\\1_insar_data\\results\\mean_vertical_displacement_STD2016.tif'
STD_rasterpath_18 = r'E:\\Thesis\\1_insar_data\\results\\mean_vertical_displacement_STD2018.tif'
DNBR_rasterpath = 'E:\\Thesis\\2_Optical_data\\DNBR_0726_0904_30m_UTM_22N.tif'
shapepath = r'E:\\Thesis\\1_insar_data\\results\\burned_area_UTM.shp'
shape_rast_outpath = 'E:\\Thesis\\1_insar_data\\results\\burned_area'
dem_path = 'E:\\Thesis\\Gimp_dem\\GIMP_DEM_30m_UTM.tif'
NDVI_rasterpath = 'E:\\Thesis\\2_Optical_data\\DNBR_0726_NDVI_30m_UTM_22N.tif'
slope_rasterpath = 'E:\\Thesis\\Gimp_dem\\gimpdem_slope_30m_UTM.tif'
aspect_rasterpath = 'E:\\Thesis\\Gimp_dem\\gimpdem_aspect_30m_UTM.tif'
rasterpath_diff = r'E:\\Thesis\\1_insar_data\\results\\mean_vertical_displacement_DIFF.tif'
std_rasterpath_diff = r'E:\\Thesis\\1_insar_data\\results\\mean_vertical_displacement_DIFF_STD.tif'
shapepath_aoi = r'E:\\Thesis\\1_insar_data\\results\\AOI_polygon_py.shp'
shape_rast_out_aoi = r'E:\\Thesis\\1_insar_data\\results\\AOI_polygon_py'


def pipeline_1(rasterpath, DNBR_rasterpath, shapepath, shape_rast_outpath,STD_rasterpath, NDVI_rasterpath, height_rasterpath):
    src_rast = gdal.Open(rasterpath)
    src_ds = ogr.Open(shapepath)
    if src_ds == None:
        print ('nonetype shapefile')
    else:
        src_lyr = src_ds.GetLayer()
        #xmin,xmax,ymin,ymax = src_lyr.GetExtent()
        cols = src_rast.RasterYSize
        rows = src_rast.RasterXSize
        print (cols,rows)
        #src_ext=xmin,ymin,xmax,ymax
        featList = range(src_lyr.GetFeatureCount())
        for feature_iteration in featList:
            xoff,yoff,xcount,ycount = rasterizer(feature_iteration,cols,rows,src_rast,src_lyr,shape_rast_outpath)

            print(str(xoff) + ' and ' + str(yoff))
            print(str(xcount) + ' and ' + str(ycount))
            if yoff >= 0:
                yoff = (yoff-ycount)
            elif yoff <= 0:
                yoff = (cols + yoff) -ycount

            extracted_values_displacement, mean_disp , boolean , img= extract_values(rasterpath,shape_rast_outpath, ycount, xcount, xoff, yoff)

            extracted_values_DNBR, mean, boolean, img = extract_values(DNBR_rasterpath, shape_rast_outpath, ycount, xcount, xoff,yoff)

            extracted_values_STD, mean_std, boolean, img = extract_values(STD_rasterpath, shape_rast_outpath, ycount, xcount, xoff, yoff)

            extracted_values_NDVI, mean, boolean, img = extract_values(NDVI_rasterpath, shape_rast_outpath, ycount, xcount, xoff, yoff)

            extracted_values_height, mean, boolean, img = extract_values(height_rasterpath, shape_rast_outpath, ycount, xcount, xoff, yoff)

            soccer_fields = len(extracted_values_displacement[np.where(extracted_values_DNBR > 0.1)])

            a = extracted_values_displacement[0] # is np.nan
            a= -999
            print (a)
            c = np.where(extracted_values_displacement == a)
            dnbr_points_up = extracted_values_DNBR[np.where((extracted_values_displacement > a) & (extracted_values_NDVI >= 0.1 ) & (extracted_values_STD <= 10))]#| extracted_values_displacement <= 0)] ### or veranderen in streepje
            disp_points_up = extracted_values_displacement[np.where((extracted_values_displacement > a) & (extracted_values_NDVI >= 0.1 ) & (extracted_values_STD <= 10) )] #  | extracted_values_displacement <= 0)]
            STD_points_up = extracted_values_STD[np.where((extracted_values_displacement > a) & (extracted_values_NDVI >= 0.1 ) & (extracted_values_STD <= 10))]

            # mean_std = np.mean(STD_points_up)

            # dnbr_points_down = extracted_values_DNBR[np.where((extracted_values_displacement <= 0 ) & (extracted_values_NDVI >= 0.4 ))]#| extracted_values_displacement <= 0)] ### or veranderen in streepje
            # disp_points_down = extracted_values_displacement[np.where((extracted_values_displacement <= 0) & (extracted_values_NDVI >= 0.4 ))] #  | extracted_values_displacement <= 0)]
            # STD_points_down = extracted_values_STD[np.where((extracted_values_displacement <= 0) & (extracted_values_NDVI >= 0.4 ))]
            #
            # dnbr_points =np.asarray(np.concatenate((dnbr_points_up,dnbr_points_down)), dtype =np.float32)
            # disp_points = np.asarray(np.concatenate((disp_points_up,disp_points_down)),dtype =np.float32)
            # STD_points = np.asarray(np.concatenate((STD_points_up,STD_points_down)),dtype =np.float32)

            dnbr_points =dnbr_points_up
            disp_points = disp_points_up
            STD_points = STD_points_up

            # print (np.nanmean(disp_points) + 'this is the nanmean total')

            disp_points_scatter = disp_points[np.where(dnbr_points >= 0.10)]
            dnbr_points_scatter = dnbr_points[np.where(dnbr_points >= 0.10)]

            # fig = plt.scatter(dnbr_points[np.where(dnbr_points > 0.2)],disp_points[np.where(dnbr_points > 0.2)])
            #print (np.nanmean(disp_points) + 'this is the nanmean total')

            #compute min/maxof the dnbr to make quantiles
            dnbr_min = min(dnbr_points)
            dnbr_max = max(dnbr_points)
            part_size = (np.abs(dnbr_min)+ np.abs(dnbr_max)) /4
            quantiles = np.arange(dnbr_min,dnbr_max, part_size)
            quantiles2 = [-0.100 , 0.100, 0.270, 0.660, 0.800]

            enhanced_regrowth = np.nanmean(disp_points[np.where(dnbr_points < quantiles2[0])])
            oo = np.nanmean((disp_points[np.where((dnbr_points < quantiles2[1]) & (dnbr_points > quantiles2[0]))])) #,(disp_points[np.where(dnbr_points > quantiles2[0])]))
            low_severity =np.nanmean((disp_points[np.where((dnbr_points < quantiles2[2]) & (dnbr_points > quantiles2[1]))]))
            moderate_severity = np.nanmean((disp_points[np.where((dnbr_points < quantiles2[3]) & (dnbr_points > quantiles2[2]))]))
            high_severity = np.nanmean(disp_points[np.where((dnbr_points < quantiles2[4]) & (dnbr_points > quantiles2[3]))])
            severe_severity = np.nanmean(disp_points[np.where(dnbr_points > quantiles2[4])])

            STD_enhanced_regrowth = np.nanmean(STD_points[np.where(dnbr_points < quantiles2[0])])
            STD_oo = np.nanmean((STD_points[np.where((dnbr_points < quantiles2[1]) & (dnbr_points > quantiles2[0]))])) #,(disp_points[np.where(dnbr_points > quantiles2[0])]))
            STD_low_severity =np.nanmean((STD_points[np.where((dnbr_points < quantiles2[2]) & (dnbr_points > quantiles2[1]))]))
            STD_moderate_severity = np.nanmean((STD_points[np.where((dnbr_points < quantiles2[3]) & (dnbr_points > quantiles2[2]))]))
            STD_high_severity = np.nanmean(STD_points[np.where((dnbr_points < quantiles2[4]) & (dnbr_points > quantiles2[3]))])
            STD_severe_severity = np.nanmean(STD_points[np.where(dnbr_points > quantiles2[4])])

            STD_enhanced_regrowth = np.nanstd(disp_points[np.where(dnbr_points < quantiles2[0])])
            STD_oo = np.nanstd((disp_points[np.where((dnbr_points < quantiles2[1]) & (dnbr_points > quantiles2[0]))])) #,(disp_points[np.where(dnbr_points > quantiles2[0])]))
            STD_low_severity =np.nanstd((disp_points[np.where((dnbr_points < quantiles2[2]) & (dnbr_points > quantiles2[1]))]))
            STD_moderate_severity = np.nanstd((disp_points[np.where((dnbr_points < quantiles2[3]) & (dnbr_points > quantiles2[2]))]))
            STD_high_severity = np.nanstd(disp_points[np.where((dnbr_points < quantiles2[4]) & (dnbr_points > quantiles2[3]))])
            STD_severe_severity = np.nanstd(disp_points[np.where(dnbr_points > quantiles2[4])])


            STD_items = (STD_enhanced_regrowth, STD_oo, STD_low_severity, STD_moderate_severity, STD_high_severity, STD_severe_severity)

            n1 = len(disp_points[np.where(dnbr_points < quantiles2[0])])
            n2 = len(disp_points[np.where((dnbr_points < quantiles2[1]) & (dnbr_points > quantiles2[0]))])
            n3 = len(disp_points[np.where((dnbr_points < quantiles2[2]) & (dnbr_points > quantiles2[1]))])
            n4 = len(disp_points[np.where((dnbr_points < quantiles2[3]) & (dnbr_points > quantiles2[2]))])
            n5 = len(disp_points[np.where(dnbr_points > quantiles2[3])])
            n6 = len(disp_points[np.where(dnbr_points > quantiles2[4])])

            print(enhanced_regrowth, n1)
            print(oo,n2)
            print(low_severity,n3)
            print(moderate_severity, n4)
            print(high_severity, n5)
            print(severe_severity,n6)
            # for part in quantiles:

            return mean_disp, enhanced_regrowth, n1, oo, n2, low_severity, n3, moderate_severity,n4, high_severity, n5, severe_severity, n6, STD_items, mean_std, disp_points, dnbr_points

total_disp_mean16, enhanced_regrowth16, n116, oo16, n216, low_severity16, n316, moderate_severity16, n416, high_severity16, n516, severe_severity16, n616,STD_items_16, mean_std_16, disp_points16,dnbr_points16 = pipeline_1(rasterpath_16, DNBR_rasterpath, shapepath, shape_rast_outpath,STD_rasterpath_16, NDVI_rasterpath, dem_path)
total_disp_mean18, enhanced_regrowth18, n118, oo18, n218, low_severity18, n318, moderate_severity18, n418, high_severity18, n518, severe_severity18, n618, STD_items_18, mean_std_18, disp_points18, dnbr_points18 = pipeline_1(rasterpath_18, DNBR_rasterpath, shapepath, shape_rast_outpath,STD_rasterpath_18, NDVI_rasterpath, dem_path)

plt.style.use('ggplot')
# fig = plt.scatter(dnbr_points18[np.where(dnbr_points18 > 0.1)], disp_points18[np.where(dnbr_points18 > 0.1)])

total_disp_mean16_v2 = np.nanmean(disp_points16[np.where(dnbr_points16 > 0.1)])
total_disp_mean18_v2 = np.nanmean(disp_points18[np.where(dnbr_points18 > 0.1)])

## extracted dnbr en displacement nu vergelijken
ind_name = ['enh', 'unb' , 'low', 'mod', 'high', 'sev']
items = (enhanced_regrowth18,oo18,low_severity18,moderate_severity18,high_severity18,severe_severity18)
width = 0.35

fig, ax = plt.subplots()
ind = np.arange(len(ind_name))  # the x locations for the groups
rects1 = ax.bar(ind- width/2, items, width,
                label='burned')
# rects2 = ax.bar(ind + width/2, women_means, width, yerr=women_std,
#                 label='Women')
ax.set_ylabel('Mean displacement vel 2018 (mm/Y)')
ax.set_xlabel('DNBR burn severity')
ax.set_title('')
ax.set_xticks(ind)
ax.set_xticklabels(ind_name)
ax.legend()
plt.show()

fig, ax = plt.subplots()
x= dnbr_points18[np.where((dnbr_points18 > 0.1)& (dnbr_points18 <0.95))]
y = disp_points18[np.where((dnbr_points18 > 0.1)& (dnbr_points18 < 0.95))]
ax.scatter(x,y)
z = np.polyfit(x, y, 1)
p = np.poly1d(z)
plt.plot(x,p(x),"b--")
plt.title("y=%.6fx+%.6f"%(z[0],z[1]))
yfit = z[0] * x + z[1]
yresid = y - yfit
SSresid = np.sum(pow(yresid,2))
SStotal = len(y) * np.var(y)
rsq = 1 - SSresid/SStotal
slope,intercept,r_value,p_value,std_err = stats.linregress(x,y)
rsq  = pow(r_value,2)
# print ('rsquared value DNBR = ' + str(rsq))
ax.text(0.15,40,'Rsq = ' + str(rsq))
ax.text(0.15,36,'P = ' + str(p_value)[0:6])
ax.set_ylabel('Mean displacement vel 2018 (mm/Y)')
ax.set_xlabel('DNBR burn severity')
ax.set_xticks([0.100, 0.270, 0.660, 0.800, 1.00])
ax.set_xticklabels(['0.1-low', '0.27-mod', '0.66-high', '0.80-ex', '1.0'])
plt.show()


burned_area_normalized_difference_year = (total_disp_mean18 - total_disp_mean16)#/total_disp_mean16
enhanced_regrowth_normalized_difference_year = (enhanced_regrowth18 - enhanced_regrowth16)#/enhanced_regrowth16
unburned_normalized_difference_year =  (oo18- oo16)#/oo16
low_severity_normalized_difference_year = (low_severity18 - low_severity16)#/ low_severity16
moderate_severity_normalized_difference_year = (moderate_severity18 - moderate_severity16)#/moderate_severity16
high_severity_normalized_difference_year = (high_severity18 - high_severity16)#/ high_severity16
severe_severity_normalized_difference_year = (severe_severity18 - severe_severity16)#/severe_severity16

print(enhanced_regrowth_normalized_difference_year, unburned_normalized_difference_year, low_severity_normalized_difference_year, moderate_severity_normalized_difference_year, high_severity_normalized_difference_year, severe_severity_normalized_difference_year)

ind_name = ['enh', 'unb' , 'low', 'mod', 'high' , 'ex']
items = (enhanced_regrowth_normalized_difference_year, unburned_normalized_difference_year, low_severity_normalized_difference_year, moderate_severity_normalized_difference_year, high_severity_normalized_difference_year, severe_severity_normalized_difference_year)
width = 0.35

fig, ax = plt.subplots()
ind = np.arange(len(ind_name))  # the x locations for the groups
rects1 = ax.bar(ind- width/2, items, width,
                label='burned')
# rects2 = ax.bar(ind + width/2, women_means, width, yerr=women_std,
#                 label='Women')
ax.set_ylabel('Mean displacement velocity change 2016 - 2018 (mm/Y)')
ax.set_xlabel('DNBR burn severity classes')
ax.set_title('')
ax.set_xticks(ind)
ax.set_xticklabels(ind_name)
ax.legend()
plt.show()

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# shapepath_compare_burn = r'E:\\Thesis\\1_insar_data\\results\\burned_area_UTM.shp'
# shape_rast_outpath_compare_burn =r'E:\\Thesis\\1_insar_data\\results\\burned_area_UTM'
# total_disp_mean16_burn, enhanced_regrowth16_burn, n116_burn, oo16_burn, n216_burn, low_severity16_burn, n316_burn, moderate_severity16_burn, n416_burn, high_severity16_burn, n516_burn, severe_severity16_burn, n616_burn, STD_items_16_burn, mean_std_16_burn, disp_points16_burn,dnbr_points16_burn = pipeline_1(rasterpath_16, DNBR_rasterpath, shapepath_compare_burn, shape_rast_outpath_compare_burn, STD_rasterpath_18, NDVI_rasterpath, dem_path)
# total_disp_mean18_burn, enhanced_regrowth18_burn, n118_burn, oo18_burn, n218_burn, low_severity18_burn, n318_burn, moderate_severity18_burn, n418_burn, high_severity18_burn, n518_burn, severe_severity18_burn, n618_burn, STD_items_18_burn, mean_std_18_burn, disp_points18_burn,dnbr_points18_burn = pipeline_1(rasterpath_18, DNBR_rasterpath, shapepath_compare_burn, shape_rast_outpath_compare_burn, STD_rasterpath_16, NDVI_rasterpath, dem_path)


shapepath_compare_normal = r'E:\\Thesis\\1_insar_data\\results\\AOI_polygon_py.shp'
shape_rast_outpath_compare_normal = r'E:\\Thesis\\1_insar_data\\results\\AOI_polygon_py'
total_disp_mean16_normal, enhanced_regrowth16_normal, n116_normal, oo16_normal, n216_normal, low_severity16_normal, n316_normal, moderate_severity16_normal, n416_normal, high_severity16_normal, n516_normal, severe_severity16_normal, n616_normal, STD_items_16_normal, mean_std_16_normal, disp_points16_normal,dnbr_points16_normal = pipeline_1(rasterpath_16, DNBR_rasterpath, shapepath_compare_normal, shape_rast_outpath_compare_normal,STD_rasterpath_16, NDVI_rasterpath, dem_path)
total_disp_mean18_normal, enhanced_regrowth18_normal, n118_normal, oo18_normal, n218_normal, low_severity18_normal, n318_normal, moderate_severity18_normal, n418_normal, high_severity18_normal, n518_normal, severe_severity18_normal, n618_normal, STD_items_18_normal, mean_std_18_normal, disp_points18_normal,dnbr_points18_normal = pipeline_1(rasterpath_18, DNBR_rasterpath, shapepath_compare_normal, shape_rast_outpath_compare_normal,STD_rasterpath_18, NDVI_rasterpath, dem_path)

disp_points18_normal_sum = np.sum(disp_points18_normal)
disp_points16_normal_sum = np.sum(disp_points16_normal)
disp_points18_normal_len = len(disp_points18_normal)
disp_points16_normal_len =len(disp_points16_normal)

disp_points18_burn_sum = np.sum(disp_points18)
disp_points16_burn_sum = np.sum(disp_points16)
disp_points18_burn_len = len(disp_points18)
disp_points16_burn_len =len(disp_points16)

compare_sum_18 = disp_points18_normal_sum - disp_points18_burn_sum
compare_sum_16 = disp_points16_normal_sum - disp_points16_burn_sum
compare_len_18 = disp_points18_normal_len - disp_points18_burn_len
compare_len_16 = disp_points16_normal_len - disp_points16_burn_len

compare_mean_18 = compare_sum_18/compare_len_18
compare_mean_16 = compare_sum_16/compare_len_16

compare_diff = compare_mean_18 - compare_mean_16
compare_diff_burn = total_disp_mean18_v2 - total_disp_mean16_v2

diff_year_16  = total_disp_mean16_v2 - compare_mean_16
diff_year_18 = total_disp_mean18_v2 - compare_mean_18

print(burned_area_normalized_difference_year)
print(compare_diff)


shapepath_compare_normal = r'E:\\Thesis\\1_insar_data\\results\\AOI_polygon_py.shp'
shape_rast_outpath_compare_normal = r'E:\\Thesis\\1_insar_data\\results\\AOI_polygon_py'
# total_disp_mean16_normal, enhanced_regrowth16_normal, n116_normal, oo16_normal, n216_normal, low_severity16_normal, n316_normal, moderate_severity16_normal, n416_normal, high_severity16_normal, n516_normal, severe_severity16_normal, n616_normal, STD_items_16_normal, mean_std_16_normal, disp_points16_normal,dnbr_points16_normal = pipeline_1(rasterpath_diff, DNBR_rasterpath, shapepath_compare_normal, shape_rast_outpath_compare_normal,STD_rasterpath_16, NDVI_rasterpath, dem_path)
total_disp_mean18, enhanced_regrowth18, n118, oo18, n218, low_severity18, n318, moderate_severity18, n418, high_severity18, n518, severe_severity18, n618, STD_items_18, mean_std_18, disp_points18, dnbr_points18 = pipeline_1(rasterpath_diff, DNBR_rasterpath, shapepath, shape_rast_outpath,std_rasterpath_diff, NDVI_rasterpath, dem_path)

fig, ax = plt.subplots()
x= dnbr_points18[np.where((dnbr_points18 > 0.1)& (dnbr_points18 <0.95))]
y = disp_points18[np.where((dnbr_points18 > 0.1)& (dnbr_points18 < 0.95))]
ax.scatter(x,y)
z = np.polyfit(x, y, 1)
p = np.poly1d(z)
plt.plot(x,p(x),"b--")
plt.title("y=%.6fx+%.6f"%(z[0],z[1]))
yfit = z[0] * x + z[1]
yresid = y - yfit
SSresid = np.sum(pow(yresid,2))
SStotal = len(y) * np.var(y)
rsq = 1 - SSresid/SStotal
slope,intercept,r_value,p_value,std_err = stats.linregress(x,y)
rsq  = pow(r_value,2)
# print ('rsquared value DNBR = ' + str(rsq))
ax.text(0.15,34,'Rsq = ' + str(rsq))
ax.text(0.15,39,'P = ' + str(p_value)[0:6])
ax.set_ylabel('velocity difference 2016 2018 (mm/Y)')
ax.set_xlabel('DNBR burn severity')
ax.set_xticks([0.100, 0.270, 0.660, 0.800, 1.00])
ax.set_xticklabels(['0.1-low', '0.27-mod', '0.66-high', '0.80-ex', '1.0'])
plt.show()

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def pipeline_dem(rasterpath, DNBR_rasterpath, shapepath, shape_rast_outpath, STD_rasterpath):
    src_rast = gdal.Open(rasterpath)
    src_ds = ogr.Open(shapepath)
    if src_ds == None:
        print ('nonetype shapefile')
    else:
        src_lyr = src_ds.GetLayer()
        #xmin,xmax,ymin,ymax = src_lyr.GetExtent()
        cols = src_rast.RasterYSize
        rows = src_rast.RasterXSize
        print (cols,rows)
        #src_ext=xmin,ymin,xmax,ymax
        featList = range(src_lyr.GetFeatureCount())
        for feature_iteration in featList:
            xoff,yoff,xcount,ycount = rasterizer(feature_iteration,cols,rows,src_rast,src_lyr,shape_rast_outpath)

            if yoff >= 0:
                yoff = (yoff-ycount)
            elif yoff <= 0:
                yoff = (cols + yoff) -ycount

            extracted_values_displacement, mean_disp , boolean , img= extract_values(rasterpath,shape_rast_outpath, ycount, xcount, xoff, yoff)

            extracted_values_DNBR, mean, boolean, img = extract_values(DNBR_rasterpath, shape_rast_outpath, ycount, xcount, xoff,yoff)

            extracted_values_STD, mean_std, boolean, img = extract_values(STD_rasterpath, shape_rast_outpath, ycount, xcount, xoff, yoff)

            mean_disp = np.mean(extracted_values_displacement[np.where(extracted_values_displacement > -999)])

            a = extracted_values_displacement[0] # is np.nan
            print (a)
            a=-999
            c = np.where(extracted_values_displacement == a)
            dnbr_points_up = extracted_values_DNBR[np.where((extracted_values_displacement > a ) & (extracted_values_STD <= 10))]#| extracted_values_displacement <= 0)] ### or veranderen in streepje
            disp_points_up = extracted_values_displacement[np.where((extracted_values_displacement > a) & (extracted_values_STD <= 10))] #  | extracted_values_displacement <= 0)]
            # dnbr_points_down = extracted_values_DNBR[np.where(extracted_values_displacement <= 0 )]#| extracted_values_displacement <= 0)] ### or veranderen in streepje
            # disp_points_down = extracted_values_displacement[np.where(extracted_values_displacement <= 0)] #  | extracted_values_displacement <= 0)]
            #
            #
            # dnbr_points =np.asarray(np.concatenate((dnbr_points_up,dnbr_points_down)), dtype =np.float32)
            # disp_points = np.asarray(np.concatenate((disp_points_up,disp_points_down)),dtype =np.float32)

            dnbr_points = dnbr_points_up
            disp_points = disp_points_up

            #plt.scatter(dnbr_points,disp_points)
            # plt.show()
            #print (np.nanmean(disp_points) + 'this is the nanmean total')

            #compute min/maxof the dnbr to make quantiles
            dnbr_min = min(dnbr_points)
            dnbr_max = max(dnbr_points)
            part_size = (np.abs(dnbr_min)+ np.abs(dnbr_max)) /7
            quantiles2 = np.arange((dnbr_min + part_size),dnbr_max, part_size)
            # quantiles2 = [-0.100 , 0.100, 0.270, 0.660, 0.800]

            enhanced_regrowth = np.nanmean(disp_points[np.where(dnbr_points < quantiles2[0])])
            oo = np.nanmean((disp_points[np.where((dnbr_points < quantiles2[1]) & (dnbr_points > quantiles2[0]))])) #,(disp_points[np.where(dnbr_points > quantiles2[0])]))
            low_severity =np.nanmean((disp_points[np.where((dnbr_points < quantiles2[2]) & (dnbr_points > quantiles2[1]))]))
            moderate_severity = np.nanmean((disp_points[np.where((dnbr_points < quantiles2[3]) & (dnbr_points > quantiles2[2]))]))
            high_severity = np.nanmean(disp_points[np.where((dnbr_points < quantiles2[4]) & (dnbr_points > quantiles2[3]))])
            severe_severity = np.nanmean(disp_points[np.where(dnbr_points > quantiles2[4])])

            n1 = len(disp_points[np.where(dnbr_points < quantiles2[0])])
            n2 = len(disp_points[np.where((dnbr_points < quantiles2[1]) & (dnbr_points > quantiles2[0]))])
            n3 = len(disp_points[np.where((dnbr_points < quantiles2[2]) & (dnbr_points > quantiles2[1]))])
            n4 = len(disp_points[np.where((dnbr_points < quantiles2[3]) & (dnbr_points > quantiles2[2]))])
            n5 = len(disp_points[np.where(dnbr_points > quantiles2[3])])
            n6 = len(disp_points[np.where(dnbr_points > quantiles2[4])])

            print(enhanced_regrowth, n1)
            print(oo,n2)
            print(low_severity,n3)
            print(moderate_severity, n4)
            print(high_severity, n5)
            print(severe_severity,n6)
            # for part in quantiles:

            return mean_disp, enhanced_regrowth, n1, oo, n2, low_severity, n3, moderate_severity,n4, high_severity, n5, severe_severity, n6, quantiles2, dnbr_points,disp_points


plt.style.use('ggplot')

total_disp_mean16, low_height_16 , n116, low_med_height_16, n216, med_height_16, n316, med_high_height_16, n416, high_height_16, n516, real_high_height_16, n616, quantiles2, height_data_16, disp_data_16 = pipeline_dem(rasterpath_16, dem_path, shapepath_aoi, shape_rast_out_aoi, STD_rasterpath_16)
total_disp_mean18, low_height_18 , n116, low_med_height_18, n216, med_height_18, n316, med_high_height_18, n416, high_height_18, n516, real_high_height_18, n616, quantiles2, height_data_18, disp_data_18 = pipeline_dem(rasterpath_18, dem_path, shapepath_aoi, shape_rast_out_aoi, STD_rasterpath_18)


low_height = np.mean((low_height_16,low_height_18))
low_med_height = np.mean((low_med_height_16,low_med_height_18))
med_height = np.mean((med_height_16,med_height_18))
med_high_height = np.mean((med_high_height_16,med_high_height_18))
high_height = np.mean((high_height_16,high_height_18))
real_high_height = np.mean((real_high_height_16,real_high_height_18))

ind_name = ['0', int(quantiles2[0]) , int(quantiles2[1]), int(quantiles2[2]), int(quantiles2[3]) ,int(quantiles2[4])]
items = (low_height, low_med_height, med_height, med_high_height, high_height, real_high_height)
width = 0.35

fig, ax = plt.subplots()
ind = np.arange(len(ind_name))  # the x locations for the groups
rects_height = ax.bar(ind- width/2, items, width,
                label='')
# rects2 = ax.bar(ind + width/2, women_means, width, yerr=women_std,
#                 label='Women')
ax.set_ylabel('Mean displacement velocities 2016 & 2018 (mm/Y)')
ax.set_xlabel('Height per class (m)')
ax.set_title('')
ax.set_xticks(ind)
ax.set_xticklabels(ind_name)
ax.legend()
plt.show()



fig, ax = plt.subplots()
x= (np.concatenate((height_data_16,height_data_18)))
y = (np.concatenate((disp_data_16,disp_data_18)))
ax.scatter(x,y)
z = np.polyfit(x, y, 1)
p = np.poly1d(z)
plt.plot(x,p(x),"b--")
plt.title("y=%.6fx+%.6f"%(z[0],z[1]))
yfit = z[0] * x + z[1]
yresid = y - yfit
SSresid = np.sum(pow(yresid,2))
SStotal = len(y) * np.var(y)
rsq = 1 - SSresid/SStotal
slope,intercept,r_value,p_value,std_err = stats.linregress(x,y)
rsq  = pow(r_value,2)
# print ('rsquared value DNBR = ' + str(rsq))
ax.text(15,45,'Rsq = ' + str(rsq))
ax.text(15,38,'P = ' + str(p_value)[0:6])
ax.set_ylabel('Mean displacement velocities 2016 & 2018 (mm/Y)')
ax.set_xlabel('Height (m)')
# ax.set_xticks([0.100, 0.270, 0.660, 0.800, 1.00])
# ax.set_xticklabels(['0.1-low', '0.27-mod', '0.66-high', '0.80-ex', '1.0'])
plt.show()


#----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def pipeline_NDVI(rasterpath, DNBR_rasterpath, shapepath, shape_rast_outpath, STD_rasterpath):
    src_rast = gdal.Open(rasterpath)
    src_ds = ogr.Open(shapepath)
    if src_ds == None:
        print ('nonetype shapefile')
    else:
        src_lyr = src_ds.GetLayer()
        #xmin,xmax,ymin,ymax = src_lyr.GetExtent()
        cols = src_rast.RasterYSize
        rows = src_rast.RasterXSize
        print (cols,rows)
        #src_ext=xmin,ymin,xmax,ymax
        featList = range(src_lyr.GetFeatureCount())
        for feature_iteration in featList:
            xoff,yoff,xcount,ycount = rasterizer(feature_iteration,cols,rows,src_rast,src_lyr,shape_rast_outpath)

            print(str(xoff) + ' and ' + str(yoff))
            print(str(xcount) + ' and ' + str(ycount))
            if yoff >= 0:
                yoff = (yoff - ycount)
            elif yoff <= 0:
                yoff = (cols + yoff) - ycount

            extracted_values_displacement, mean_disp , boolean , img= extract_values(rasterpath,shape_rast_outpath, ycount, xcount, xoff, yoff)

            extracted_values_DNBR, mean, boolean, img = extract_values(DNBR_rasterpath, shape_rast_outpath, ycount, xcount, xoff,yoff)

            extracted_values_STD, mean_std, boolean, img = extract_values(STD_rasterpath, shape_rast_outpath, ycount,xcount, xoff, yoff)

            a = -999 # extracted_values_displacement[0] # is np.nan
            print (a)
            c = np.where(extracted_values_displacement == a)
            dnbr_points_up = extracted_values_DNBR[np.where((extracted_values_displacement > -999 ) & (extracted_values_STD <= 10)) ]#| extracted_values_displacement <= 0)] ### or veranderen in streepje
            disp_points_up = extracted_values_displacement[np.where((extracted_values_displacement > -999) & (extracted_values_STD <= 10))] #  | extracted_values_displacement <= 0)]
            # dnbr_points_down = extracted_values_DNBR[np.where(extracted_values_displacement <= 0 )]#| extracted_values_displacement <= 0)] ### or veranderen in streepje
            # disp_points_down = extracted_values_displacement[np.where(extracted_values_displacement <= 0)] #  | extracted_values_displacement <= 0)]

            # dnbr_points =  np.asarray(np.concatenate((dnbr_points_up,dnbr_points_down)), dtype =np.float32)
            # disp_points = np.asarray(np.concatenate((disp_points_up,disp_points_down)),dtype =np.float32)

            dnbr_points =  dnbr_points_up
            disp_points = disp_points_up

            #print (np.nanmean(disp_points) + 'this is the nanmean total')

            #compute min/maxof the dnbr to make quantiles
            dnbr_min = min(dnbr_points)
            dnbr_max = max(dnbr_points)
            part_size = (np.abs(dnbr_min)+ np.abs(dnbr_max)) /7
            # quantiles2 = np.arange((dnbr_min + part_size),dnbr_max, part_size)
            quantiles2 =  [0.0 , 0.10, 0.40, 0.50, 0.60, 0.65, 0.80] # [0.0 , 0.10, 0.20, 0.30, 0.60] #### extra klassen maken

            enhanced_regrowth = np.nanmean(disp_points[np.where(dnbr_points < quantiles2[0])])
            oo = np.nanmean((disp_points[np.where((dnbr_points < quantiles2[1]) & (dnbr_points > quantiles2[0]))])) #,(disp_points[np.where(dnbr_points > quantiles2[0])]))
            low_severity =np.nanmean((disp_points[np.where((dnbr_points < quantiles2[2]) & (dnbr_points > quantiles2[1]))]))
            moderate_severity = np.nanmean((disp_points[np.where((dnbr_points < quantiles2[3]) & (dnbr_points > quantiles2[2]))]))
            high_severity = np.nanmean(disp_points[np.where((dnbr_points < quantiles2[4]) & (dnbr_points > quantiles2[3]))])
            higher_severity = np.nanmean(disp_points[np.where((dnbr_points < quantiles2[5]) & (dnbr_points > quantiles2[4]))])
            extreme_severity = np.nanmean(disp_points[np.where((dnbr_points < quantiles2[6]) & (dnbr_points > quantiles2[5]))])
            severe_severity = np.nanmean(disp_points[np.where(dnbr_points > quantiles2[6])])

            n1 = len(disp_points[np.where(dnbr_points < quantiles2[0])])
            n2 = len(disp_points[np.where((dnbr_points < quantiles2[1]) & (dnbr_points > quantiles2[0]))])
            n3 = len(disp_points[np.where((dnbr_points < quantiles2[2]) & (dnbr_points > quantiles2[1]))])
            n4 = len(disp_points[np.where((dnbr_points < quantiles2[3]) & (dnbr_points > quantiles2[2]))])
            n5 = len(disp_points[np.where(dnbr_points > quantiles2[3])])
            n6 = len(disp_points[np.where(dnbr_points > quantiles2[4])])

            print(enhanced_regrowth, n1)
            print(oo,n2)
            print(low_severity,n3)
            print(moderate_severity, n4)
            print(high_severity, n5)
            print(severe_severity,n6)
            # for part in quantiles:

            return mean_disp, enhanced_regrowth, n1, oo, n2, low_severity, n3, moderate_severity,n4, high_severity, n5, severe_severity, n6, quantiles2, higher_severity, extreme_severity, dnbr_points, disp_points

total_disp_mean16, misc_16 , n116, bare_rock_16, n216, small_veg_16, n316, bush_veg_16, n416, bush_grass_veg_16, n516, thick_veg_16, n616, quantiles2, higher_severity_16, extreme_severity_16, ndvi_points_16, disp_vel_points_16 = pipeline_NDVI(rasterpath_16, NDVI_rasterpath, shapepath_aoi, shape_rast_out_aoi, STD_rasterpath_16)
total_disp_mean18, misc_18 , n116, bare_rock_18, n216, small_veg_18, n316, bush_veg_18, n416, bush_grass_veg_18, n516, thick_veg_18, n616, quantiles2, higher_severity_18, extreme_severity_18, ndvi_points_18, disp_vel_points_18 = pipeline_NDVI(rasterpath_18, NDVI_rasterpath, shapepath_aoi, shape_rast_out_aoi, STD_rasterpath_18)

misc = misc_16 # misc_16 #np.mean((misc_16, misc_18)) #
bare_rock = bare_rock_16 # bare_rock_16 #np.mean((bare_rock_16, bare_rock_18)) #
small_veg =small_veg_16 #  small_veg_16# np.mean((small_veg_16, small_veg_18)) #
bush_veg = bush_veg_16 # bush_veg_16 #np.mean((bush_veg_16, bush_veg_18)) #
bush_grass_veg = bush_grass_veg_16 #bush_grass_veg_16# np.mean((bush_grass_veg_16, bush_grass_veg_18)) #
sev_veg =  higher_severity_16 # higher_severity_16 #np.mean((higher_severity_16, higher_severity_18)) #
extreme_veg = extreme_severity_16 # extreme_severity_16 #np.mean((extreme_severity_16, extreme_severity_18))#
thick_veg = thick_veg_16 # thick_veg_16 #np.mean((thick_veg_16, thick_veg_18)) #

plt.style.use('ggplot')
ind_name = [0.0 , 0.10, 0.40, 0.50, 0.6, 0.65, 0.80]
ind_name_2 = [-1, 0.0, 0.10, 0.40, 0.50, 0.6, 0.65, 0.80,1.0]
items = (misc, bare_rock, small_veg, bush_veg, bush_grass_veg,sev_veg,extreme_veg, thick_veg)
width = 0.35

fig, ax = plt.subplots()
ind = np.arange(len(items))  # the x locations for the groups
rects_height = ax.bar(ind- width/2, items, width,
                label='')
# rects2 = ax.bar(ind + width/2, women_means, width, yerr=women_std,
#                 label='Women')
ax.set_ylabel('Mean displacement velocities 2016 (mm/Y)')
ax.set_xlabel('NDVI classes')
ax.set_title('')
ax.set_xticks(ind)
ax.set_xticklabels(ind_name_2)
ax.legend()
plt.show()


ndvi_points_16 = ndvi_points_16[np.where(ndvi_points_16 > 0.1)]
disp_vel_points_16 = disp_vel_points_16[np.where(ndvi_points_16 > 0.1)]
ndvi_points_18 = ndvi_points_18[np.where(ndvi_points_18 > 0.1)]
disp_vel_points_18 = disp_vel_points_18[np.where(ndvi_points_18 > 0.1)]

fig, ax = plt.subplots()
x= ndvi_points_16 #(np.concatenate((ndvi_points_16,ndvi_points_18)))
y = disp_vel_points_16 #(np.concatenate((disp_vel_points_16,disp_vel_points_18)))
ax.scatter(x,y)
z = np.polyfit(x, y, 1)
p = np.poly1d(z)
plt.plot(x,p(x),"b--")
plt.title("y=%.6fx+%.6f"%(z[0],z[1]))
yfit = z[0] * x + z[1]
yresid = y - yfit
SSresid = np.sum(pow(yresid,2))
SStotal = len(y) * np.var(y)
rsq = 1 - SSresid/SStotal
slope,intercept,r_value,p_value,std_err = stats.linregress(x,y)
rsq  = pow(r_value,2)
# print ('rsquared value DNBR = ' + str(rsq))
ax.text(0.15,20,'Rsq = ' + str(rsq))
ax.text(0.15,16,'P = ' + str(p_value)[0:6])
ax.set_ylabel('Mean displacement velocities 2016 (mm/Y)')
ax.set_xlabel('NDVI')
ax.set_xticks([0.10, 0.40, 0.50, 0.60, 0.65, 0.80, 1.0])
# ax.set_xticklabels(['0.1-small', '0.40-bush', '0.60-grass', '0.65-grass2', '0.8-thick','1.0'])
plt.show()


total_disp_mean18, misc_18 , n116, bare_rock_18, n216, small_veg_18, n316, bush_veg_18, n416, bush_grass_veg_18, n516, thick_veg_18, n616, quantiles2, higher_severity_18, extreme_severity_18, ndvi_points_18, disp_vel_points_18 = pipeline_NDVI(DNBR_rasterpath, NDVI_rasterpath, shapepath, shape_rast_outpath, STD_rasterpath_18)

# ndvi_points_18 = ndvi_points_18[np.where(ndvi_points_18 > 0.10)]
# disp_vel_points_18 = disp_vel_points_18[np.where(ndvi_points_18 > 0.10)]

fig, ax = plt.subplots()
x= ndvi_points_18 #(np.concatenate((ndvi_points_16,ndvi_points_18)))
y = disp_vel_points_18 #(np.concatenate((disp_vel_points_16,disp_vel_points_18)))
ax.scatter(x,y)
z = np.polyfit(x, y, 1)
p = np.poly1d(z)
plt.plot(x,p(x),"b--")
plt.title("y=%.6fx+%.6f"%(z[0],z[1]))
yfit = z[0] * x + z[1]
yresid = y - yfit
SSresid = np.sum(pow(yresid,2))
SStotal = len(y) * np.var(y)
rsq = 1 - SSresid/SStotal
slope,intercept,r_value,p_value,std_err = stats.linregress(x,y)
rsq  = pow(r_value,2)
# print ('rsquared value DNBR = ' + str(rsq))
ax.text(-0.9,1,'Rsq = ' + str(rsq))
ax.text(-0.9,0.8,'P = ' + str(p_value)[0:6])
ax.set_ylabel('DNBR Burn severity')
ax.set_xlabel('NDVI')
ax.set_xticks([-1.0, -0.5, 0.0,  0.40, 0.60, 0.80, 1.0])
# ax.set_xticklabels(['0.1-small', '0.40-bush', '0.60-grass', '0.65-grass2', '0.8-thick','1.0'])
plt.show()

#----------------------------------------------------------------------------------------------------------------------------------------------------
#
def pipeline_aspect(rasterpath, DNBR_rasterpath, shapepath, shape_rast_outpath,slope_path, STD_rasterpath):
    src_rast = gdal.Open(rasterpath)
    src_ds = ogr.Open(shapepath)
    if src_ds == None:
        print ('nonetype shapefile')
    else:
        src_lyr = src_ds.GetLayer()
        #xmin,xmax,ymin,ymax = src_lyr.GetExtent()
        cols = src_rast.RasterYSize
        rows = src_rast.RasterXSize
        print (cols,rows)
        #src_ext=xmin,ymin,xmax,ymax
        featList = range(src_lyr.GetFeatureCount())
        for feature_iteration in featList:
            xoff,yoff,xcount,ycount = rasterizer(feature_iteration,cols,rows,src_rast,src_lyr,shape_rast_outpath)

            print(str(xoff) + ' and ' + str(yoff))
            print(str(xcount) + ' and ' + str(ycount))
            if yoff >= 0:
                yoff = (yoff - ycount)
            elif yoff <= 0:
                yoff = (cols + yoff) - ycount

            extracted_values_displacement, mean_disp , boolean , img= extract_values(rasterpath,shape_rast_outpath, ycount, xcount, xoff, yoff)

            extracted_values_DNBR, mean, boolean, img = extract_values(DNBR_rasterpath, shape_rast_outpath, ycount, xcount, xoff,yoff)

            extracted_values_slope, mean_slope, boolean, img = extract_values(slope_path, shape_rast_outpath, ycount,xcount, xoff, yoff)

            extracted_values_STD, mean_std, boolean, img = extract_values(STD_rasterpath, shape_rast_outpath, ycount,xcount, xoff, yoff)

            # mean_disp = np.mean(extracted_values_slope[np.where(extracted_values_slope > -999)])

            a = -999 #extracted_values_displacement[0] # is np.nan
            print (a)
            c = np.where(extracted_values_displacement == a)
            dnbr_points_up = extracted_values_DNBR[np.where((extracted_values_displacement > a )  & (extracted_values_STD <= 10))]#| extracted_values_displacement <= 0)] ### or veranderen in streepje
            disp_points_up = extracted_values_displacement[np.where((extracted_values_displacement > a)& (extracted_values_STD <= 10))] #  | extracted_values_displacement <= 0)]
            slope_points_up = extracted_values_slope[np.where((extracted_values_displacement > a)& (extracted_values_STD <= 10))]

            # dnbr_points_down = extracted_values_DNBR[np.where(extracted_values_displacement <= 0 )]#| extracted_values_displacement <= 0)] ### or veranderen in streepje
            # disp_points_down = extracted_values_displacement[np.where(extracted_values_displacement <= 0)] #  | extracted_values_displacement <= 0)]
            # slope_points_down = extracted_values_slope[np.where(extracted_values_displacement <= 0)]

            # dnbr_points_1 =np.asarray(np.concatenate((dnbr_points_up,dnbr_points_down)), dtype =np.float32)
            # disp_points_1 = np.asarray(np.concatenate((disp_points_up,disp_points_down)),dtype =np.float32)
            # slope_points = np.asarray(np.concatenate((slope_points_up,slope_points_down)),dtype =np.float32)

            dnbr_points_1 = dnbr_points_up
            disp_points_1 = disp_points_up
            slope_points = slope_points_up

            dnbr_points = dnbr_points_1[np.where(slope_points >= 7.5)]
            disp_points = disp_points_1[np.where(slope_points >= 7.5)]
            #print (np.nanmean(disp_points) + 'this is the nanmean total')

            #compute min/maxof the dnbr to make quantiles
            dnbr_min = min(dnbr_points)
            dnbr_max = max(dnbr_points)
            part_size = (np.abs(dnbr_min)+ np.abs(dnbr_max)) /7
            # quantiles2 = np.arange((dnbr_min + part_size),dnbr_max, part_size)
            quantiles2 = [45,90,135,180,225,270,315]

            NNW = np.nanmean(disp_points[np.where(dnbr_points < quantiles2[0])])
            WNW = np.nanmean((disp_points[np.where((dnbr_points < quantiles2[1]) & (dnbr_points > quantiles2[0]))])) #,(disp_points[np.where(dnbr_points > quantiles2[0])]))
            WSW = np.nanmean((disp_points[np.where((dnbr_points < quantiles2[2]) & (dnbr_points > quantiles2[1]))]))
            SSW = np.nanmean((disp_points[np.where((dnbr_points < quantiles2[3]) & (dnbr_points > quantiles2[2]))]))
            SSE = np.nanmean(disp_points[np.where((dnbr_points < quantiles2[4]) & (dnbr_points > quantiles2[3]))])
            ESE = np.nanmean(disp_points[np.where((dnbr_points < quantiles2[5]) & (dnbr_points > quantiles2[4]))])
            ENE = np.nanmean(disp_points[np.where((dnbr_points < quantiles2[6]) & (dnbr_points > quantiles2[5]))])
            NNE = np.nanmean(disp_points[np.where(dnbr_points > quantiles2[6])])


            n1 = len(disp_points[np.where(dnbr_points < quantiles2[0])])
            n2 = len(disp_points[np.where((dnbr_points < quantiles2[1]) & (dnbr_points > quantiles2[0]))])
            n3 = len(disp_points[np.where((dnbr_points < quantiles2[2]) & (dnbr_points > quantiles2[1]))])
            n4 = len(disp_points[np.where((dnbr_points < quantiles2[3]) & (dnbr_points > quantiles2[2]))])
            n5 = len(disp_points[np.where((dnbr_points < quantiles2[4]) & (dnbr_points > quantiles2[3]))])
            n6 = len(disp_points[np.where((dnbr_points < quantiles2[5]) & (dnbr_points > quantiles2[4]))])
            n7 = len(disp_points[np.where((dnbr_points < quantiles2[6]) & (dnbr_points > quantiles2[5]))])
            n8 = len(disp_points[np.where(dnbr_points > quantiles2[6])])

            # for part in quantiles:

            return mean_disp, NNW, n1, WNW, n2, WSW, n3, SSW,n4, SSE, n5, ESE, n6, ENE, n7 , NNE, n8, quantiles2, slope_points,disp_points_1

total_disp_mean16, misc_16 , n116, bare_rock_16, n216, small_veg_16, n316, bush_veg_16, n416, bush_grass_veg_16, n516, thick_veg_16, n616, ENE_16, n716, NNE_16, n816, quantiles2,slope_points16, disp_points16 = pipeline_aspect(rasterpath_16, aspect_rasterpath, shapepath_aoi, shape_rast_out_aoi, slope_rasterpath, STD_rasterpath_16)
total_disp_mean18, misc_18 , n116, bare_rock_18, n216, small_veg_18, n316, bush_veg_18, n416, bush_grass_veg_18, n516, thick_veg_18, n618, ENE_18, n718, NNE_18, n818, quantiles2,slope_points18, disp_points18 = pipeline_aspect(rasterpath_18, aspect_rasterpath, shapepath_aoi, shape_rast_out_aoi, slope_rasterpath, STD_rasterpath_18)

mean_slope = np.mean(slope_points16[np.where(slope_points16 > -999)])

misc = np.mean((misc_16, misc_18))
bare_rock = np.mean((bare_rock_16, bare_rock_18))
small_veg = np.mean((small_veg_16, small_veg_18))
bush_veg = np.mean((bush_veg_16, bush_veg_18))
bush_grass_veg = np.mean((bush_grass_veg_16, bush_grass_veg_18))
thick_veg = np.mean((thick_veg_16, thick_veg_18))
ENE = np.mean((ENE_16, ENE_18))
NNE = np.mean((NNE_16, NNE_18))

plt.style.use('ggplot')
ind_name = ['0', int(quantiles2[0]) , int(quantiles2[1]), int(quantiles2[2]), int(quantiles2[3]) ,int(quantiles2[4]), int(quantiles2[5]), int(quantiles2[6])]
items = (misc, bare_rock, small_veg, bush_veg, bush_grass_veg, thick_veg, ENE, NNE)
width = 0.35

fig, ax = plt.subplots()
ind = np.arange(len(ind_name))  # the x locations for the groups
rects_aspect = ax.bar(ind- width/2, items, width,
                label='')
# rects2 = ax.bar(ind + width/2, women_means, width, yerr=women_std,
#                 label='Women')
ax.set_ylabel('Mean displacement velocities 2016 & 2018 (mm/Y)')
ax.set_xlabel('Aspect (deg)')
ax.set_title('')
ax.set_xticks(ind)
ax.set_xticklabels(['NNW', 'WNW', 'WSW', 'SSW', 'SSE', 'ESE', 'ENE', 'NNE'])
ax.legend()
plt.show()

fig, ax = plt.subplots()
x= (np.concatenate((slope_points16,slope_points18)))
y = (np.concatenate((disp_points16,disp_points18)))
ax.scatter(x,y)
z = np.polyfit(x, y, 1)
p = np.poly1d(z)
plt.plot(x,p(x),"r--")
plt.title("y=%.6fx+%.6f"%(z[0],z[1]))
yfit = z[0] * x + z[1]
yresid = y - yfit
SSresid = np.sum(pow(yresid,2))
SStotal = len(y) * np.var(y)
rsq = 1 - SSresid/SStotal
slope,intercept,r_value,p_value,std_err = stats.linregress(x,y)
rsq  = pow(r_value,2)
# print ('rsquared value DNBR = ' + str(rsq))
ax.text(1,46,'Rsq = ' + str(rsq))
ax.text(1,40,'P = ' + str(p_value)[0:6])
ax.set_ylabel('Mean displacement velocities 2016 & 2018 (mm/Y)')
ax.set_xlabel('Slope (deg)')
# ax.set_xticks([-1.0, -0.5, 0.0,  0.40, 0.60, 0.80, 1.0])
# ax.set_xticklabels(['0.1-small', '0.40-bush', '0.60-grass', '0.65-grass2', '0.8-thick','1.0'])
plt.show()