from googleplaces import GooglePlaces, types, lang
import json
import sys

MY_API_KEY = open(sys.argv[1]).readlines()[0]

from googleplaces import GooglePlaces, types, lang

google_places = GooglePlaces(MY_API_KEY)
out_json = {'names':[],'locations':[],'place_ids':[]}
# You may prefer to use the text_search API, instead.
query_result = google_places.nearby_search(
        location='Seattle, Washington', 
        radius=150, types=['restaurant'])

if query_result.has_attributions:
    print query_result.html_attributions

for place in query_result.places:
    # Returned places from a query are place summaries.
    #print place.name
    out_json['names'].append(place.name)
    #print place.geo_location
    out_json['locations'].append(place.geo_location)
    #print place.place_id
    out_json['place_ids'].append(place.place_id)

    # The following method has to make a further API call.
##    place.get_details()
    # Referencing any of the attributes below, prior to making a call to
    # get_details() will raise a googleplaces.GooglePlacesAttributeError.
##    print place.details # A dict matching the JSON response from Google.
##    print place.local_phone_number
##    print place.international_phone_number
##    print place.website
##    print place.url

    # Getting place photos

##    for photo in place.photos:
        # 'maxheight' or 'maxwidth' is required
##        photo.get(maxheight=500, maxwidth=500)
        # MIME-type, e.g. 'image/jpeg'
##        photo.mimetype
        # Image URL
##        photo.url
        # Original filename (optional)
##        photo.filename
        # Raw image data
##        photo.data

#output = json.dumps(out_json)

print out_json
