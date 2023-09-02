import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
from pymongo import MongoClient
from datetime import datetime
import logging
import sys

def connect_mongo(type):
    global collection
    client = MongoClient("mongodb://localhost:27017/")
    db = client["land"]
    collection = db["data_"]
    

connect_mongo("abc")
# Open the JSON file
with open('02_1.json') as file:
    # Load the JSON data
    data = json.load(file)
    test = data["cat1"]["searchResults"]["mapResults"]

print (len(test))

for one in test:
    body = {}
    # MLS Number, Status, Listing Date, Listing Price, Sold Date, Sold Price, Location, Acres, Days on Market, HOA/Month, URL, Latitude, Longitude, Price Per Arce
    print(one)
    body['MLS_number'] = one['zpid']
    body['status'] = one["statusText"]
    body['listingDate'] = ''
    body['listingPrice'] = ''
    body['soldData'] = ''
    body['soldPrice'] = ''
    body['location'] = one['address']
    body["acres"] = one["area"]
    body['dayOfMarket']=one['variableData']['text']
    body['HOA/Month'] = ''
    body['URL'] = "https://www.zillow.com" + one['detailUrl']
    body['latitude'] = one['latLong']["latitude"]
    body['longitude'] = one['latLong']["longitude"]
    if(one['area'] != 0 and one['price'] != ''):
        body['pricePerArce'] = float(one['price']) / one["area"]
    body['price'] = one['price']
    body['title'] = one['address']
    if collection.find_one({'url': one['detailUrl']}) is None:    
        collection.insert_one(one)

# Access the data
# print(data)
