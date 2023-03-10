import arcpy

# Access the desired ArcGIS Pro project
aprx = arcpy.mp.ArcGISProject(r"C:\Users\JohnsonN35\project_path\project_name.aprx")

# Create a Map object
chMap = aprx.listMaps("Odor Diary Reports - by Date")[0]

# Create a Layout object
lyt = aprx.listLayouts("Odor Diary Reports - by Date NEW")[0]

# Create a Mapframe object
mf = lyt.listElements("MAPFRAME_ELEMENT", "Primary Map")[0]

# Access layers to be definition queried, create a new field to hold timestamp-less dates, and bring over dates from original date field

# Access layers
odorLocations = chMap.listLayers("Odor Perception")[0]
sympLocations = chMap.listLayers("Health Symptoms")[0]

# Create a new field called DateNoTimestamp, but make it nullable and not required
# Odor Perception and Health Symptoms are the same layer, just symbolized differently, so only need 1 new field
# https://pro.arcgis.com/en/pro-app/2.9/tool-reference/data-management/add-field.htm
# arcpy.management.AddField(odorLocations, "DateNoTimestamp", "DATE", None, None, None, "", "NULLABLE", "NON_REQUIRED", "")

# Bring over dates from original date field to fill in new date field
# Note that there are still more parameters after the code block, which is itself a parameter
# https://pro.arcgis.com/en/pro-app/2.9/tool-reference/data-management/calculate-field.htm
# Code block: https://support.esri.com/en/technical-article/000025447
arcpy.management.CalculateField(odorLocations, "DateNoTimestamp", "timestamp(!DStartDate1!)", "PYTHON3", """from datetime import datetime

def timestamp(mydate):
 date = mydate
 strdate = date.strftime("%Y/%m/%d")
 finaldate = datetime.strptime(strdate,"%Y/%m/%d")
 return finaldate""", "TEXT", "NO_ENFORCE_DOMAINS")

# Set the extent of the map with a bookmark
chBkmk = mf.map.listBookmarks("Canvassing Area")[0]
mf.zoomToBookmark(chBkmk)

# Get all unique date values in the data (will be used later for definition query), then print
with arcpy.da.SearchCursor(odorLocations, ["DateNoTimestamp"]) as cursor:
    dateList = sorted({row[0] for row in cursor})
print(dateList)

# Loop through dateList, assign components of each date to a variable (could also skip and just do this right in the PDF path),
# create a definition query for each date, then print to PDF using date component variables

for date in dateList:
    day = str(date.day)
    month = str(date.month)
    year = str(date.year)
    odorLocations.definitionQuery = "DateNoTimestamp = timestamp '{}'".format(date)
    sympLocations.definitionQuery = "DateNoTimestamp = timestamp '{}'".format(date)
    dynamicDate = lyt.listElements("TEXT_ELEMENT", "DynamicDate")[0]
    dynamicDate.text = "Diary entries recorded on \n"+month+"/"+day+"/"+year+" for the previous day*"
    lyt.exportToPDF(r"C:\Users\JohnsonN35\project_path\export_"+month+"-"+day+"-"+year+".pdf", 300, "BEST", 
                    False, "ADAPTIVE", True, "LAYERS_ONLY", False, 100, False, True, True, False)
    print(month,"/",day,"/",year + " has printed")

# Clear definition query
odorLocations.definitionQuery = None
sympLocations.definitionQuery = None

# Clear date from text element so it's not confusing (otherwise it'll have the last date that was definition queried)
dynamicDate.text = "Diary entries recorded on \n"+"__/__/____"+" for the previous day*"
