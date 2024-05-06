"""
    - This script is used to upload the scraped data to AWS S3 bucket.
    
    - The script uses the 'boto3' library to connect to AWS S3 bucket.

    - The script uses the 'config.ini' file to fetch the required AWS credentials.

    Input:
        None
    
    Output:
        Uploads the scraped data to AWS S3 bucket.
    
    Usage:
        python3 scraping/load_data.py       
"""

# Importing the required libraries
import os
import boto3
from botocore.exceptions import NoCredentialsError
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

# Function to upload files to AWS S3
def upload_files(path):

    # Creating a 'boto' session connection
    session = boto3.Session(
        aws_access_key_id=ACCESS,
        aws_secret_access_key=SECRET,
        region_name=REGION
    )

    # Setting the resource and bucket name
    s3 = session.resource('s3')
    bucket = s3.Bucket(BUCKET)
 
    # Iterate through the specified directory
    for subdir, dirs, files in os.walk(path):

        # Upload each file in the specified directory
        for file in files:

            # Get full path of all files
            full_path = os.path.join(subdir, file)

            # Put the files in S3 bucket
            with open(full_path, 'rb') as data:
                bucket.put_object(Key=full_path[len(path):], Body=data)
 
# Main function
if __name__ == "__main__":
    
    # Calling the function to upload data by specifying the directory location
    upload_files('data/json/')
