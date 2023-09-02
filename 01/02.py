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
url = "https://www.zillow.com/search/GetSearchPageState.htm?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22mapBounds%22%3A%7B%22west%22%3A-96.71318908349609%2C%22east%22%3A-96.31150146142578%2C%22south%22%3A32.06188046423129%2C%22north%22%3A32.30247563517963%7D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22sortSelection%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22isAllHomes%22%3A%7B%22value%22%3Atrue%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A12%2C%22usersSearchTerm%22%3A%22%22%7D&wants={%22cat1%22:[%22listResults%22,%22mapResults%22],%22cat2%22:[%22total%22]}&requestId=3"

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en,en-US;q=0.9,ko;q=0.8",
    # "Cookie": "x-amz-continuous-deployment-state=AYABeLnVBdsnYpi3mihGDnr97lcAPgACAAFEAB1kM2Jsa2Q0azB3azlvai5jbG91ZGZyb250Lm5ldAABRwAVRzA3MjU1NjcyMVRZRFY4RDcyVlpWAAEAAkNEABpDb29raWUAAACAAAAADKBPwMAimvHnzPCxBAAwHlMeNaLhgZ1bf4Ba4o58nz2XQjoEXV3YplCsH%2FmuJmYy5L4SYM0HPvkveORXREJ1AgAAAAAMAAQAAAAAAAAAAAAAAAAAAJsxvijjair3ggpa3+sv3B7%2F%2F%2F%2F%2FAAAAAQAAAAAAAAAAAAAAAQAAAAzdVuqF44uV4y4JMmioaFZjmz0JM4I+8RzU5HbU; JSESSIONID=B10BF49C71369FE094A0EDEE4C5B9679; zguid=24|%24e37993c5-8106-4c94-9b85-91214c27acdb; zgsession=1|4228eacd-4919-4ec6-8f86-a36ab8e41336; x-amz-continuous-deployment-state=AYABeMac1TUNUfSbct%2FgVe%2FCdhcAPgACAAFEAB1kM2Jsa2Q0azB3azlvai5jbG91ZGZyb250Lm5ldAABRwAVRzA3MjU1NjcyMVRZRFY4RDcyVlpWAAEAAkNEABpDb29raWUAAACAAAAADFfTlC5b7qPVeOvoMAAwunVPMn6TIZXcr91gelbabBYYPs5enNOZgtiStFMphfQh99evjAwe36rYfBnkuOCYAgAAAAAMAAQAAAAAAAAAAAAAAAAAAAKx0JdDMgmGK+KwfokTgjz%2F%2F%2F%2F%2FAAAAAQAAAAAAAAAAAAAAAQAAAAwlrX0YTLxyWRWPTpUIyqdotaeKDf+ZEbQindBB; AWSALB=4DQJPRA1DkxEUhA9JCrtlkVqQ3Xe7YfyZbw1nr7hAJpM0v46K2Z+gg/bOX4im13wrJuGwX5wRqS3I2BDQT2EGvAwg51+qZlwgKLvPAillRGl7IYbFvY1EPHaQiDc; AWSALBCORS=4DQJPRA1DkxEUhA9JCrtlkVqQ3Xe7YfyZbw1nr7hAJpM0v46K2Z+gg/bOX4im13wrJuGwX5wRqS3I2BDQT2EGvAwg51+qZlwgKLvPAillRGl7IYbFvY1EPHaQiDc",
    "Sec-Ch-Ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform":"Windows",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

collection = None
logger = logging.getLogger(__name__)

def main():
    # Define the request payload
    type_url = url #.format(type, price, price + 100)
    print(type_url)

    # Send a POST request with the payload as raw data
    response = requests.get(type_url, headers=headers)
    print(type_url)
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Extract the data from the response
        data = response.json()

        print(data)
        return

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
        print("Error: Failed to retrieve data from the API", response.status_code)

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
    main()
    # for one in types:
    #     for pri in range(0, 100000, 100):
    #         print(one, pri)
    #         connect_mongo(one)
    #         main(one, pri)
    
    