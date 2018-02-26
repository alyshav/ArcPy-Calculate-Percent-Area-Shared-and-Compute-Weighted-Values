#########################################################
#
#   ADA to FSA converter part 2 by Aly van D
#   Adds weighted census data to Canadian FSAs
#   Using output matrix generated in part 1
#
#########################################################

import arcpy
import numpy as np
from functools import partial

##### * User Inputs * #####

# Change base path & shapefile names here:
basepath = "E:/455Data_Feb24/"
censusdatafilename = "ada_census_2.shp" # ADA Shapefile with previously joined census data
fsafilename = "fsa_frequency.shp" # FSA Shapefile
fsawithfields = "FSA_FC_with_fields_feb25_2018_2.shp" #to be created in this script, but you can change the name here

#generate field names corresponding to demographics columns extracted
field_names = ["COL"+str(a) for a in range(6,22)]

##### Variables & Temp File Name Construction #####

fid = "FID"
matrix = []
adaFC = basepath + censusdatafilename
fsaFC = basepath + fsafilename
fsaFCwithfields = basepath + fsawithfields

###### MAIN ######
    
arcpy.env.workspace = basepath + "datasets.mdb"

arcpy.MakeFeatureLayer_management(fsaFC, "fsa_lyr")
arcpy.MakeFeatureLayer_management(adaFC, "ada_lyr")
FSACount = int(arcpy.GetCount_management(fsaFC).getOutput(0))
ADACount = int(arcpy.GetCount_management(adaFC).getOutput(0))

# GENERATE WEIGHTED DEMOGRAPHICS FOR EACH FSA

arcpy.Delete_management(fsaFCwithfields)
arcpy.CopyFeatures_management(fsaFC, fsaFCwithfields)
desc = arcpy.Describe(fsaFC)
addfield = partial(arcpy.AddField_management,fsaFCwithfields,field_type="DOUBLE",field_precision=19,field_scale=6)
for field in field_names:
    addfield(field)

newWeightedValuesAll = []

fidcounter = 0
with open(basepath+'output.csv') as f:
    lines=f.readlines()
    for line in lines:
        weightcols = np.fromstring(line, dtype=float, sep=',')          
        weightindices = np.nonzero(weightcols) #obtain non-zero indices from each row 

        values = []
        weights = []
        #select ADAs matching the stored indices:
        for ada_fid in weightindices[0]:
            weights.append(weightcols[ada_fid])
            for row in arcpy.da.SearchCursor(adaFC, field_names, "FID = "+str(ada_fid)):            
                values.append(row)

        newWeightedValues = []
        for i in range(len(field_names)):
            numerator = 0
            denominator = 0
            for j in range(len(values)):            
                numerator+=(values[j][i]*weights[j])
            newWeightedValues.append(numerator)
        fidcounter+=1
        newWeightedValuesAll.append(newWeightedValues)

# ADD WEIGHTED FIELDS TO THE NEW SHAPEFILE

fidcounter = 0
cursor = arcpy.da.UpdateCursor(fsaFCwithfields, field_names)
for row in cursor:
    for f in range(len(field_names)):
        row[f] = newWeightedValuesAll[fidcounter][f]
    cursor.updateRow(row)
    fidcounter+=1

######### Code written by Alysha van Duynhoven ##########
#   if you have any questions, contact
#   Alysha van Duynhoven (alyshavand@gmail.com)
#   www.github.com/alyshav      alyshav.com
#########################################################
