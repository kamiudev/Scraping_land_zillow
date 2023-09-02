import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
from pymongo import MongoClient
from datetime import datetime
import logging
import sys

# Define the API endpoint URL
types = ("is-active", "is-under-contract", "is-active", "is-sold")
url = "https://www.land.com/api/property/search/0/United-States/{}/{}-{}/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

collection = None
logger = logging.getLogger(__name__)

def main(type, price):
    # Define the request payload
    type_url = url.format(type, price, price + 100)
    print(type_url)

    # Send a POST request with the payload as raw data
    response = requests.get(type_url, headers=headers)
    print(type_url)
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Extract the data from the response
        data = response.json()

        resultCount = data['searchResults']['totalCount']
        pageCount = resultCount // 25 + 1
        print (resultCount, pageCount)

        for page in range(1, pageCount+1):
            new_url = type_url + "page-{}/".format(page)
            response = requests.get(new_url, headers=headers)      
            data = response.json()

            for one in data['searchResults']['propertyResults']:
                # print (one)
                
                body = {}
                # MLS Number, Status, Listing Date, Listing Price, Sold Date, Sold Price, Location, Acres, Days on Market, HOA/Month, URL, Latitude, Longitude, Price Per Arce
                
                body['MLS_number'] = one['accountId']
                body['status'] = type
                body['listingDate'] = ''
                body['listingPrice'] = ''
                body['soldData'] = ''
                body['soldPrice'] = ''
                body['location'] = one['city'] + " " + one['state']
                body["acres"] = one["acres"]
                body['dayOfMarket']=one['insertDate']
                body['HOA/Month'] = ''
                body['URL'] = "https://www.land.com" + one['canonicalUrl']
                body['latitude'] = one['latitude']
                body['longitude'] = one['longitude']
                if(one['acres'] != 0):
                    body['pricePerArce'] = float(one['price']) / one["acres"]
                body['price'] = one['price']
                body['title'] = one['title']

                if collection.find_one({'url': one['canonicalUrl']}) is None:    
                    collection.insert_one(body)
                    # print(one['url'])
                else:
                    msg = "url '{}' - Content with the same url already exists.".format(one['canonicalUrl'])
                    logger.error(msg)
                    print(msg)                
        
        # print(len(data['Results']))
    else:
        print("Error: Failed to retrieve data from the API")

def connect_mongo(type):
    global collection
    client = MongoClient("mongodb://localhost:27017/")
    db = client["land"]
    collection = db["data_{}".format(type)]

def log_init():
    file_handler = logging.FileHandler('error_land.com_.log')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

if __name__ == "__main__": 
    log_init()
    for one in types:
        for pri in range(0, 100000, 100):
            print(one, pri)
            connect_mongo(one)
            main(one, pri)
    
    