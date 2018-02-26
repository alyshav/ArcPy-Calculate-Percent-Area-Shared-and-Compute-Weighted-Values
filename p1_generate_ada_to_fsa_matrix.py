#########################################################
#
#   Single-Threaded ADA to FSA converter part 1
#   by Aly van D
#   Creates matrix of shared percent area shared by
#   each ADA and FSA
#
#########################################################

import arcpy
import numpy as np
import time
import csv

##### * User Inputs * #####

# Change base path & shapefile names here:
basepath = "E:/455Data_Feb24/"
# Base shapefile we want to add weighted data to:
fsafilename = "fsa_frequency.shp" # FSA Shapefile
# Base shapefile we want to obtain weighted data from:
censusdatafilename = "ada_census.shp" # ADA Shapefile with previously joined census data

##### Variables & Temp File Name Instantiation #####

fid = "FID"
matrix = []
adaFC = basepath + censusdatafilename
fsaFC = basepath + fsafilename
tempIntersection = "in_memory/tempIntersection" 
tempIntersectionWithArea = "in_memory/temp_intersect_area"
tempFSAlyr = "temp_fsa_lyr"
tempADAlyr = "temp_ada_lyr"
fsalyr = "fsa_lyr"
adalyr = "ada_lyr"

##### Functions #####

# cleanEnv: removes all temp files and layers
def cleanEnv():
    try:
        arcpy.Delete_management(tempFSAlyr) 
        arcpy.Delete_management(tempADAlyr)
        arcpy.Delete_management(tempIntersection)
        arcpy.Delete_management(tempIntersectionWithArea)
    except Exception as e:
        print("Error deleting layers: ", e)
    print("Environment cleaned.")

###### MAIN ######

start = time.time()
    
arcpy.env.workspace = basepath + "datasets.mdb"

# Clean temp files & Create Layers        
cleanEnv()
arcpy.MakeFeatureLayer_management(fsaFC, fsalyr)
arcpy.MakeFeatureLayer_management(adaFC, adalyr)
FSACount = int(arcpy.GetCount_management(fsaFC).getOutput(0))
ADACount = int(arcpy.GetCount_management(adaFC).getOutput(0))

print("FSA Count: ", FSACount)
print("ADA Count: ", ADACount)
start = time.strftime('%X %x %Z')

with open(basepath+"output.csv", "w") as f:
    writer = csv.writer(f, delimiter=',', lineterminator='\n')
    # Iterates through each FSA feature:
    for fsaentry_fid in range(FSACount):
        fidkey = "FID = " + str(fsaentry_fid)
        matrix = np.zeros(ADACount)
        print(fidkey) #display where we are at during processing

        FSAselection = arcpy.SelectLayerByAttribute_management(fsalyr, "NEW_SELECTION", fidkey)
        ADAselection = arcpy.SelectLayerByLocation_management(adalyr, "INTERSECT", FSAselection)
        arcpy.MakeFeatureLayer_management(FSAselection, tempFSAlyr)

        area = 0
        for a in arcpy.da.SearchCursor(FSAselection, "Shape_Area"):
            area = float(a[0])

        # Iterates through the ADAs that intersect with the currently selected FSA:    
        for row in arcpy.SearchCursor(ADAselection):
            adaentry_fid = row.fid
            arcpy.MakeFeatureLayer_management(ADAselection, tempADAlyr)
            tempselect = arcpy.SelectLayerByAttribute_management(tempADAlyr, "NEW_SELECTION", "FID = "+str(adaentry_fid))
            inputFeatures = [tempFSAlyr, tempADAlyr]
            try:
                arcpy.Intersect_analysis(inputFeatures, tempIntersection, "ALL", "", "INPUT")
                if arcpy.management.GetCount(tempIntersection)[0] == "1":
                    arcpy.CalculateAreas_stats(tempIntersection, tempIntersectionWithArea)
                    for a in arcpy.da.SearchCursor(tempIntersectionWithArea, "F_AREA"):                        
                        matrix[int(adaentry_fid)] = a[0]/area
            except Exception as e:
                print("Failed operation: ", e)            
            arcpy.Delete_management(tempADAlyr)
            arcpy.Delete_management(tempIntersection)
            arcpy.Delete_management(tempIntersectionWithArea)
        arcpy.Delete_management(tempFSAlyr)
        writer.writerow(matrix)

end = time.strftime('%X %x %Z')
print("Relationship matrix processing times:")
print("Start: ", start)
print("End: ", end)

######### Code written by Alysha van Duynhoven ##########
#   if you have any questions, contact
#   Alysha van Duynhoven (alyshavand@gmail.com)
#   www.github.com/alyshav      alyshav.com
#########################################################
