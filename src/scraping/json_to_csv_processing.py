"""
    This file contains the code to process the json files and convert them into csv files.

    Input:
        JSON files that are downloaded from the AWS S3 bucket.

    Output:
        CSV file that are stored in the 'data/processed' folder.

    Usage:
        spark-submit scraping/json_to_csv_processing.py
"""

# Importing the required libraries
import sys
assert sys.version_info >= (3, 5)

from pyspark.sql import SparkSession, types
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import explode, lower
from pyspark.sql.functions import col, concat_ws, regexp_replace
import os
import shutil

def extract_year(date_str):
    """
        Extracts the year from a date string.
    """
    if date_str is None:

        return None
    
    elif len(date_str) == 4:

        return int(date_str)
    
    elif len(date_str) == 10:

        return int(date_str.split('-')[0])
    
    elif date_str == '0':

        return None
    
    else:

        return None

# Main function
def main(dir_path):
    
    # Creating sub-schema for tracks array
    tracks_schema = types.StructType([                        
                        types.StructField('id', types.StringType(), True),
                        types.StructField('name', types.StringType(), True),
                        types.StructField('artist id', types.ArrayType(types.StringType()), True),
                        types.StructField('artists', types.ArrayType(types.StringType()), True),
                        types.StructField('artist genre', types.ArrayType(types.StringType()), True),
                        types.StructField('album type', types.StringType(), True),
                        types.StructField('album id', types.StringType(), True),
                        types.StructField('album name', types.StringType(), True),
                        types.StructField('album release date', types.StringType(), True),
                        types.StructField('duration_ms', types.IntegerType(), True),
                        types.StructField('popularity', types.IntegerType(), True),
                        types.StructField('danceability', types.FloatType(), True),
                        types.StructField('energy', types.FloatType(), True),
                        types.StructField('key', types.IntegerType(), True),
                        types.StructField('loudness', types.FloatType(), True),
                        types.StructField('mode', types.IntegerType(), True),
                        types.StructField('speechiness', types.FloatType(), True),
                        types.StructField('acousticness', types.FloatType(), True),
                        types.StructField('instrumentalness', types.FloatType(), True),
                        types.StructField('liveness', types.FloatType(), True),
                        types.StructField('valence', types.FloatType(), True),
                        types.StructField('tempo', types.FloatType(), True),
                        types.StructField('time_signature', types.FloatType(), True)
                        ])

    # Creating the main schema which uses above track_schema
    schema = types.StructType([
                        types.StructField("playlist id", types.StringType(), True),
                        types.StructField("tracks", types.ArrayType(tracks_schema), True)
                    ])

    # Reads all the json files in the directory                    
    df = spark.read.schema(schema).option("encoding", "UTF-8").json(dir_path + '/*.json', multiLine = True)

    # Explode the tracks array and select the columns
    tracks_df = df.select(explode("tracks").alias("track"))

    # Selecting the columns from the tracks array
    keys = tracks_df.select("track.*").columns

    # Creating a new dataframe with the selected columns
    columns = [tracks_df["track"][key].alias(key) for key in keys]

    # Selecting the required columns
    tracks_data = tracks_df.select(columns)

    # Dropping the rows with null values
    tracks_data = tracks_data.dropna(subset=["id", "name", "artist id", "artists", "artist genre"], how='any')

    # Dropping the duplicates
    tracks_data  = tracks_data.dropDuplicates(subset=["id"])

    # Convert the artist_id and Artist_name arrays into strings by removing the brackets and commas
    tracks_data = tracks_data.withColumn("artist id", concat_ws(",", col("artist id")))
    tracks_data = tracks_data.withColumn("artists", concat_ws(",", col("artists")))
    tracks_data = tracks_data.withColumn("artist genre", concat_ws(",", col("artist genre")))
    
    # Replacing the double quotes with single quotes
    result_df = tracks_data.withColumn("name", regexp_replace("name", '"', "'"))
    result_df = result_df.withColumn("album name", regexp_replace("album name", '"', "'"))
    result_df = result_df.withColumn("artists", regexp_replace("artists", '"', "'"))

    # Converting the column names to lower case
    result_df = result_df.withColumn("name", lower(result_df["name"]))
    result_df = result_df.withColumn("artists", lower(result_df["artists"]))
    result_df = result_df.withColumn("artist genre", lower(result_df["artist genre"]))
    result_df = result_df.withColumn("album name", lower(result_df["album name"]))

    # Defining the UDF to extract the year from the album release date
    extract_year_udf = udf(extract_year, types.IntegerType())
    
    # Extracting the year from the album release date in the correct format and converting it to integer
    result_df = result_df.withColumn('album release date', extract_year_udf('album release date'))
    result_df = result_df.withColumn("album release date", col("album release date").cast("integer"))
   
    # Defining the columns names
    new_cols = ['id', 'name', 'artist_id', 'artists', 'artist_genre', 'album_type',
       'album_id', 'album_name', 'album_release_date', 'duration_ms',
       'popularity', 'danceability', 'energy', 'key', 'loudness', 'mode',
       'speechiness', 'acousticness', 'instrumentalness', 'liveness',
       'valence', 'tempo', 'time_signature']
    
    # Renaming the columns
    result_df = result_df.toDF(*new_cols)

    # Dropping the rows with null values 
    result_df = result_df.dropna(subset=["id", "name", "artist_id", "artists", "artist_genre"], how='any')
    result_df= result_df.na.drop(how='any')

    # Saving the cleaned CSV 
    result_df.coalesce(1).write.csv("data/csv/clean_data", header=True)

    os.system("mv data/csv/clean_data/part-* data/csv/clean_data/clean_data.csv")

    print('Done!')

if __name__ == '__main__':

    """
        Main function to run the code.
    """
    
    inputs = 'data/json'
    spark = SparkSession.builder.appName('data-cleaning').getOrCreate()
    assert spark.version >= '3.0'
    spark.sparkContext.setLogLevel('WARN')
    sc = spark.sparkContext
    
    if os.path.exists("data/csv/clean_data/"):
        shutil.rmtree("data/csv/clean_data/")

    main(inputs)
