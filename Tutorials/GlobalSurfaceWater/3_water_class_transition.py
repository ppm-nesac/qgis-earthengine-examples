# GitHub URL: https://github.com/giswqs/qgis-earthengine-examples/tree/master/Tutorials/GlobalSurfaceWater/3_water_class_transition.py

import ee 
from ee_plugin import Map 

###############################
# Asset List
###############################

gsw = ee.Image('JRC/GSW1_1/GlobalSurfaceWater')
occurrence = gsw.select('occurrence')
change = gsw.select("change_abs")
transition = gsw.select('transition')
roi = ee.Geometry.Polygon(
        [[[105.531921, 10.412183],
          [105.652770, 10.285193],
          [105.949401, 10.520218],
          [105.809326, 10.666006]]])
###############################
# Constants
###############################

VIS_OCCURRENCE = {
    'min': 0,
    'max': 100,
    'palette': ['red', 'blue']
}
VIS_CHANGE = {
    'min': -50,
    'max': 50,
    'palette': ['red', 'black', 'limegreen']
}
VIS_WATER_MASK = {
  'palette': ['white', 'black']
}

###############################
# Helper functions
###############################

# Create a feature for a transition class that includes the area covered.
def createFeature(transition_class_stats):
  transition_class_stats = ee.Dictionary(transition_class_stats)
  class_number = transition_class_stats.get('transition_class_value')
  result = {
      'transition_class_number': class_number,
      'transition_class_''name': lookup_names.get(class_number),
      'transition_class_''palette': lookup_palette.get(class_number),
      'area_m2': transition_class_stats.get('sum')
  }
  return ee.Feature({}, result)   # Creates a feature without a geometry.


# Create a JSON dictionary that defines piechart colors based on the
# transition class palette.
# https:#developers.google.com/chart/interactive/docs/gallery/piechart
def createPieChartSliceDictionary(fc):
  return ee.List(fc.aggregate_array("transition_class_palette")) \
    .map(lambda p: {'color': p}).getInfo()


###############################
# Calculations
###############################

# Create a dictionary for looking up names of transition classes.
lookup_names = ee.Dictionary.fromLists(
    ee.List(gsw.get('transition_class_values')).map(ee.String),
    gsw.get('transition_class_names')
)
# Create a dictionary for looking up colors of transition classes.
lookup_palette = ee.Dictionary.fromLists(
    ee.List(gsw.get('transition_class_values')).map(ee.String),
    gsw.get('transition_class_palette')
)

# Create a water mask layer, and set the image mask so that non-water areas
# are transparent.
water_mask = occurrence.gt(90).mask(1)
# # Generate a histogram object and print it to the console tab.
# histogram = ui.Chart.image.histogram({
#   'image': change,
#   'region': roi,
#   'scale': 30,
#   'minBucketWidth': 10
# })
# histogram.setOptions({
#   title: 'Histogram of surface water change intensity.'
# })
# print(histogram)

# Summarize transition classes in a region of interest.
area_image_with_transition_class = ee.Image.pixelArea().addBands(transition)
reduction_results = area_image_with_transition_class.reduceRegion(**{
  'reducer': ee.Reducer.sum().group(**{
    'groupField': 1,
    'groupName': 'transition_class_value',
  }),
  'geometry': roi,
  'scale': 30,
  'bestEffort': True,
})
print('reduction_results', reduction_results.getInfo())

# roi_stats = ee.List(reduction_results.get('groups'))

# transition_fc = ee.FeatureCollection(roi_stats.map(createFeature))
# print('transition_fc', transition_fc.getInfo())

# # Add a summary chart.
# transition_summary_chart = ui.Chart.feature.byFeature({
#     features: transition_fc,
#     xProperty: 'transition_class_name',
#     yProperties: ['area_m2', 'transition_class_number']
#   }) \
#   .setChartType('PieChart') \
#   .setOptions({
#     title: 'Summary of transition class areas',
#     slices: createPieChartSliceDictionary(transition_fc),
#     sliceVisibilityThreshold: 0  # Don't group small slices.
#   })
# print(transition_summary_chart)

###############################
# Initialize Map Location
###############################

# Uncomment one of the following statements to center the map on
# a particular location.
# Map.setCenter(-90.162, 29.8597, 10)   # New Orleans, USA
# Map.setCenter(-114.9774, 31.9254, 10) # Mouth of the Colorado River, Mexico
# Map.setCenter(-111.1871, 37.0963, 11) # Lake Powell, USA
# Map.setCenter(149.412, -35.0789, 11)  # Lake George, Australia
Map.setCenter(105.26, 11.2134, 9)     # Mekong River Basin, SouthEast Asia
# Map.setCenter(90.6743, 22.7382, 10)   # Meghna River, Bangladesh
# Map.setCenter(81.2714, 16.5079, 11)   # Godavari River Basin Irrigation Project, India
# Map.setCenter(14.7035, 52.0985, 12)   # River Oder, Germany & Poland
# Map.setCenter(-59.1696, -33.8111, 9)  # Buenos Aires, Argentina
# Map.setCenter(-74.4557, -8.4289, 11)  # Ucayali River, Peru

###############################
# Map Layers
###############################

Map.addLayer(water_mask, VIS_WATER_MASK, '90% occurrence water mask', False)
Map.addLayer(occurrence.updateMask(occurrence.divide(100)), VIS_OCCURRENCE, "Water Occurrence (1984-2015)", False)
Map.addLayer(change, VIS_CHANGE, 'occurrence change intensity', False)
Map.addLayer( transition, {}, 'Transition classes (1984-2018)')
