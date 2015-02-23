import json
from pprint import pprint
json_data=open('mcdonalds_locations.json')

data = json.load(json_data)
print len(data)
json_data.close()
