"""
    This file is used to extract concert details from Ticketmaster's API

    Input:
        Directory where the final .json will be stored

    Outputs:
        A json file containing concerts in a dictionary format

    Usage:
        python3 application/ticketmaster.py
"""

from requests import get
import json
import os
import time
from dotenv import load_dotenv


# Set up the Ticket Master credentials
dotenv_path = 'utils/.env'
load_dotenv(dotenv_path ,verbose=False)

api_key = os.getenv("TICKET_MASTER_KEY")


def api_endpoint():
    """
        function to generate endpoint to which the API will hit

        Args:
            None

        Returns:
            str: string containing endpoint URL
    """
    # Define the API endpoint URL
    endpoint_url = "https://app.ticketmaster.com/discovery/v2/events.json"

    return endpoint_url

def api_request(location, start_date, end_date, genre):
    """
        Create a function to generate API request using inputs

        Args:
            param1 (str): location where to search for events
            param2 (str): start date of your search range
            param3 (str): end date of your search range
            param4 (str): str of comma separated genres you want to search for 

        Returns:
            dict, int: return dict format of response and length of dict
    """
    # Define the parameters for the API request
    params = {

        "apikey": api_key,
        "city": location,
        "classificationName": genre,
        "sort": "date,asc",
        "startDateTime": start_date + "T00:00:00Z",
        "endDateTime": end_date + "T23:59:59Z",
        "page" : 0
    }

    # Send a GET request to the API endpoint
    endpoint_url = api_endpoint()
    response = get(endpoint_url, params=params)

    result = response.json()
    total_pages = result["page"]["totalPages"]
    total_entries = result["page"]["totalElements"]

    # Check the status code of the response
    if response.status_code == 200:

        event_data = []
        
        try:

            for page in range(total_pages):

                params["page"] = page
                response = get(endpoint_url, params=params)

                event_data += response.json()["_embedded"]["events"]

        except: 

            event_data = []

    else:

        event_data = []

        # Print an error message
        print("Error: The API request failed with status code {}".format(response.status_code))
        
    return event_data, total_entries

def get_event_features(event):
    """
        Create a function to return features of an event

        Args:
            param1 (dict): event in dictionary format
          
        Returns:
            dict: dictionary containing features of an event defined below 
    """

    # Create a dictionary called features for event
    features = {
        
        "artist_name" : None,
        "artist_image_link" : None,
        "ticket_url" : None,
        "event_start_local_date": None,
        "event_start_local_time" : None,
        "venue_name" : None,
        "address" : None,
        "city" : None,
        "postal_code" : None,
        "min_price" : 0,
        "max_price" : 0,
        "currency" : None,
        "spotify_artist_link" : None
    }

    features["artist_name"] = event["name"].title()
    features["ticket_url"] = event["url"]
    features["event_start_local_date"] = event["dates"]["start"]["localDate"]
    features["event_start_local_time"] = event["dates"]["start"]["localTime"]
    features["venue_name"] = event["_embedded"]["venues"][0]["name"]
    features["address"] = event["_embedded"]["venues"][0]["address"]["line1"]
    features["postal_code"] = event["_embedded"]["venues"][0]["postalCode"]
    features["city"] = event["_embedded"]["venues"][0]["city"]["name"]


    artist_image = event["images"]
    
    for images in artist_image:

        flag = 0
        
        if "ratio" in images:

            if images["ratio"] == "3_2":

                features["artist_image_link"] = images["url"]

                flag = 1
    
    if flag == 0:

        features["artist_image_link"] = artist_image[0]["url"]


    try:

        features["min_price"] = event["priceRanges"][0]["min"]
        features["max_price"] = event["priceRanges"][0]["max"]
        features["currency"] = event["priceRanges"][0]["currency"]
    
    except:

        features["min_price"] = 0
        features["max_price"] = 0
        features["currency"]  = None
    
    try:

        features["spotify_artist_link"] = event["_embedded"]["attractions"][0]["externalLinks"]["spotify"][0]["url"]

    except:

        features["spotify_artist_link"] = None
    
    return features

def parse_events(location, start_date, end_date, genre):

    time.sleep(2)

    events_dict = {
        "no_of_events" : None,
        "events" : []
    }

    events_list = []

    event_data, total_entries = api_request(location, start_date, end_date, genre)

    for event in event_data:
        
        try:

            event_features = get_event_features(event)

            events_list.append(event_features)
        
        except:

            print('Error!')
    
    events_dict["events"] = events_list
    events_dict["no_of_events"] = total_entries
            
    return events_dict

# defining a function to get events
def get_events(location, start_date, end_date, genre):

    start_time = time.time()

    filepath = "application/"

    # inputs
    location = location
    start_date = start_date
    end_date = end_date
    genre = genre

    # calling the function to get events
    events = parse_events(location, start_date, end_date, genre)

    # checking if there are any events
    if events["no_of_events"] == 0:
        print(404)
    else:

        while len(events["events"]) == 0:
            
            events = parse_events(location, start_date, end_date, genre)

            if len(events["events"]) == events["no_of_events"]:
                break    
    
    # saving the events to a json file
    with open("data/events_scraped.json", "w") as outfile:
        json.dump(events, outfile, ensure_ascii=False, indent=4)

    end_time = time.time()
    runtime = end_time - start_time
    print(f"Runtime: {runtime:.2f} seconds")
    