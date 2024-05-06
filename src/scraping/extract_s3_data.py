"""
    - This script is used to extract the data from AWS S3 Bucket to local machine

    - The data is then utilized for cleaning and further analytical purposes

    Input:
        None

    Output:
        Files downloaded to local machine

    Usage:
        python3 scraping/extract_s3_data.py

"""

# Importing the required libraries
import os
import sys
import boto3
import botocore
from configparser import ConfigParser

# Creating a 'config' object to access the config file
config_object = ConfigParser()
config_object.read('utils/config.ini')

# Searching for the required user in the config file
user = config_object['AWSCONSOLE']

# Fetching all the required details
ACCESS = user['ACCESS_KEY']
SECRET = user['SECRET_KEY']
BUCKET = user['BUCKET_NAME']
REGION = user['BUCKET_REGION']

# Main function
def main():

    filename = 'json_scraped/'
    os.system("cd data/json && rm -r %s" %filename)

    # Creating a 'boto' session connection
    session = boto3.Session(
        aws_access_key_id=ACCESS,
        aws_secret_access_key=SECRET,
        region_name=REGION
    )

    # Setting the resource and bucket name
    s3 = session.resource('s3')
    bucket = s3.Bucket(BUCKET)

    # Download all files in the folder
    for obj in bucket.objects.filter(Prefix='json_scraped'):
        if not obj.key.endswith('/'): # Skip directories
            bucket.download_file(obj.key, 'data/json/' + os.path.basename(obj.key))
    
if __name__ == '__main__':

    main()
