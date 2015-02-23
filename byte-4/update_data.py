__author__ = 'vikram'
from scrapy.selector import Selector

# Scrape an individual McDonalds store #
# Returns {'store_number': store_number, 'address': address, 'lat': latitude, 'lng': longitude} on success
# If McDonalds website doesn't show a store by that number, return False
# If geolocation fails, will return only 'store_number' and 'address'
#
# Things to watch out for:
#
# 1) If you see "No module named scrapy.selector", you'll need to install the scrapy library.
# See http://scrapy.org/download/ for directions how to download and install.
#
# 2) If you see errors about zope.interface, try updating zope.interface to a newer version like so:
# "pip install --upgrade zope.interface"
#    and then restart the kernel (Kernel/Restart, at the top of the notebook, above).
#
# Or, if you have troubles getting scrapy to install properly, consider switching to the
# BeautifulSoup-based scraper below

def parse_xpath(path, selector):
    try:
        return ''.join(selector.xpath(path).extract()).strip()
    except:
        return ""


import json
import urllib
import urllib2

# Geocode a street address using Google's geocoding API
# Returns {'lat': latitude, 'lng': longitude} on success
# Returns False if not found
# Raises exception if a problem occurs (such as running out of quota)
#
# Note:  Google's geolocation service is limited to around 2500 geolocations per day.  If you receive
# an error that you've run out of quota, you'll need to wait a day, or change your IP address.
#
# (For the purposes of this assignment, see below for a shortcut to download already geolocated addresses to
#  fill in your gaps)
#
#  If you run into quota limitation and don't want to wait a day, here are some ways to change your IP address:
#    - If you're on a laptop, move to a different wireless network
#    - Find an HTTP proxy at http://www.hidemyass.com/proxy-list and switch to that proxy with this python command:
#      urllib2.install_opener(urllib2.build_opener(urllib2.ProxyHandler({'http': '168.63.167.183'})))
#    - Utitlize a VPN service (e.g. Hide My Ass's "Pro VPN" account, which costs $)

def geocode(address):
    # Perform API call to maps.googleapis.com, which will return address in JSON format
    url = 'http://maps.googleapis.com/maps/api/geocode/json?%s' % urllib.urlencode(
        {'address': address, 'sensor': 'false'})
    geocode = json.loads(urllib2.urlopen(url).read())
    if geocode['status'] == 'OK' and geocode['results']:
        # Success!  Return the first result
        return geocode['results'][0]['geometry']['location']
    elif geocode['status'] <> 'ZERO_RESULTS':
        # Something failed (maybe out of quota?).  Raise an exception.
        msg = 'When trying to geocode address %s by reading url %s, received a status != OK: %s' % (
            address, url, geocode['status'])
        print msg
        raise Exception(msg)
    else:
        # No results for this address.  Return false.
        return False


def scrape_store(store_number, old_location):
    # Oddly, www.mcdonalds.com's map application redirects to www.mc<statename>.com to show store details.
    # But, lucky for us, any of the states sites seem to work for all store #s.  So let's go with PA for no particular reason.
    url = "http://www.mcpennsylvania.com/%d" % store_number

    print "Trying to fetch store# %d from %s" % (store_number, url)
    html = urllib2.urlopen(url).read()
    #print "  Read %d bytes" % len(html)

    # Using Scrapy, build an XPath selector to parse the received HTML
    selector = Selector(text=html)

    # The street address is buried in the <li> tag whose class contains the word "address" (usually address_3 but
    # sometimes address_1 and maybe others).
    # Inside that <li>, find all the <h3> tags, extract text from them, and then join together with newlines in-between.
    address = '\n'.join(selector.xpath('//li[contains(@class, "address")]/h3/text()').extract())
    name = parse_xpath('//h2[contains(@class, "storename")]/text()', selector)
    phone = parse_xpath('//div[contains(@class, "address")]/span[2]/span/text()', selector)
    image = "http://www.mcpennsylvania.com" + parse_xpath('//div[@class="address"]/img[@class="storephoto"]/@src',
                                                          selector)

    lobby_open = parse_xpath('//div[@id="lobby"]/span[@class="third"]/text()', selector)
    lobby_close = parse_xpath('//div[@id="lobby"]/span[@class="fourth"]/text()', selector)

    drive_open = parse_xpath('//div[@id="drive_thru"]/span[@class="first"]/text()', selector)
    drive_close = parse_xpath('//div[@id="drive_thru"]/span[@class="second"]/text()', selector)

    if address:
        location = {'store_number': store_number, 'address': address, 'name': name, 'phone': phone, 'image_url': image}
        if lobby_open:
            location['lobby'] = lobby_open + " " + lobby_close
            location['drive'] = drive_open + " " + drive_close
        #print '  Address is %s' % address.replace('\n', '|')
        if "lat" in old_location:
            #latlng = geocode(address)
            #print '  Geocoded to %s' % latlng
            location['lat'] = old_location['lat']
            location['lng'] = old_location['lng']
        #else:
        #    latlng = geocode(address)
        #    if latlng:
        #        location['lat'] = latlng['lat']
        #        location['lng'] = latlng['lng']
        return location
    else:
        #print '  Store not found'
        return False

#
# Functions to load and save scraped McDonalds locations to/from this local JSON file:
#

import os
import json

locations_path = os.path.expanduser('~/Work/git/kmarkiv/data/byte-4/data/mcdonalds_locations.json')
locations_path2 = os.path.expanduser('~/Work/git/kmarkiv/data/byte-4/data/mcdonalds_locations2.json')
# Read locations from your local json file.  If the file is missing, create it.
def read_or_create_locations():
    try:
        locations = json.load(open(locations_path))
        print 'Read %d locations from %s' % (len(locations), locations_path)
    except StandardError:
        locations = []
        print '%s does not exist; creating' % locations_path
        write_locations(locations)
    return locations


def read_or_create_locations2():
    try:
        locations = json.load(open(locations_path2))
        print 'Read %d locations from %s' % (len(locations), locations_path2)
    except StandardError:
        locations = []
        print '%s does not exist; creating' % locations_path
        write_locations(locations)
    return locations

# Write locations to your local json file

locations = read_or_create_locations()
locations_data = read_or_create_locations2()


def write_locations(locations):
    try:
        os.makedirs(os.path.dirname(locations_path2))
    except StandardError:
        pass
    json.dump(locations, open(locations_path2, 'w'), indent=2)
    print 'Wrote %d locations to %s' % (len(locations), locations_path2)


starting_store = 1
print locations_data[-1]['store_number']
data = locations_data
last_store = len(locations)
for store_number in range(len(locations_data), last_store + 1):
    if locations[store_number]['store_number'] > locations_data[-1]['store_number']:
        #print store_number
        location = scrape_store(locations[store_number]['store_number'], locations[store_number])
    else:
        location = locations[store_number]
    if location:
        data.append(location)
        if len(data) % 50 == 0:
            # Checkpoint:  every ten, save all locations to disk
            write_locations(data)

# Done.  Save all locations
write_locations(data)


# Done.  Save all locations
#write_locations(locations_data)

