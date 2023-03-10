# This will only work with dates, not datetimes

# REQUIRED: Set up necessary components
import arcpy

aprx = arcpy.mp.ArcGISProject(r"C:\Users\JohnsonN35\project_path\project_name.aprx")    # Access the current ArcGIS Pro project
grMap = aprx.listMaps("Map")[0]                                                         # Create a Map object from the map called Map
lyt = aprx.listLayouts("MapLayout")[0]                                                  # Create a Layout object from the layout called MapLayout
mf = lyt.listElements("MAPFRAME_ELEMENT", "Primary Map")[0]                             # Create a Mapframe object from the mapframe called Primary Map

# OPTION 1: Use the extent of a specific layer

# In the grMap Map object, search for the layer matching the name provided
grBounds = grMap.listLayers("Grand Rapids City Boundaries")[0]

# Set the camera extent to that of the aforementioned layer
# https://pro.arcgis.com/en/pro-app/2.9/arcpy/mapping/mapframe-class.htm
mf.camera.setExtent(mf.getLayerExtent(grBounds, False, True))

# OPTION 2: Use the extent of a specific bookmark
# https://pro.arcgis.com/en/pro-app/2.9/arcpy/mapping/map-class.htm

# In the Primary Map Mapframe object, search for the bookmark called "Grand Rapids" then zoom to it
grBkmk = mf.map.listBookmarks("Grand Rapids")[0]
mf.zoomToBookmark(grBkmk)

# OPTION 3: Input coordinate system extents
# https://pro.arcgis.com/en/pro-app/2.9/arcpy/classes/extent.htm

xMin = 3885856.71484248
yMin = 152887.560404714
xMax = 3903305.93367761
yMax = 173092.467258105

extent = arcpy.Extent(xMin,yMin,xMax,yMax)
mf.camera.setExtent(extent)

# REQUIRED: Access layer to be definition queried
randomLocations = grMap.listLayers("Random Locations")[0]

# Get all unique date values in the layer, then print
inTable = randomLocations  
inField = 'DATE'

with arcpy.da.SearchCursor(inTable, [inField]) as cursor:
    dateList = sorted({row[0] for row in cursor})
print(dateList)

# REQUIRED: Loop through dateList, assign components of each date to a variable (could also skip and just 
# do this right in the PDF path), create a definition query for each date, then print to PDF using date
# component variables.

for date in dateList:
    day = str(date.day)
    month = str(date.month)
    year = str(date.year)
    print(month, day, year + " is about to print")
    randomLocations.definitionQuery = "DATE = timestamp '{}'".format(date)
    dynamicDate = lyt.listElements("TEXT_ELEMENT", "DynamicDate")[0]
    dynamicDate.text = "Results on "+month+"/"+day+"/"+year
    lyt.exportToPDF(r"C:\Users\JohnsonN35\project_path\test_"+month+"-"+day+"-"+year+".pdf")

# Clear definition query
randomLocations.definitionQuery = None


