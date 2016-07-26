from googleplaces import GooglePlaces, types, lang
import json
import sys

MY_API_KEY = open(sys.argv[1]).readlines()[0]

#Using the googleplaces package to get places from Google Places
from googleplaces import GooglePlaces, types, lang

google_places = GooglePlaces(MY_API_KEY)
out_json = {'names':[],'locations':[],'place_ids':[]}
query_result = google_places.nearby_search(
        location='Seattle, Washington', 
        radius=150, types=['restaurant'])

if query_result.has_attributions:
    print query_result.html_attributions

for place in query_result.places:
    # Return names, locations and place_ids of queried results.
    out_json['names'].append(place.name)
    out_json['locations'].append(place.geo_location)
    out_json['place_ids'].append(place.place_id)

print out_json
