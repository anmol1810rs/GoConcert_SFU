# CMPT 733 G100 - Final Project - Spring 2023

**Team Name:  Data Hunters**

**Team Members:**

| Name | Student ID | Computing ID |
| :--- | :--- | :--- |
| Rithik Agarwal | 301560443 | raa72@sfu.ca | 
| Anmol Malhotra | 301546554 | ama302@sfu.ca | 
| Hardev Khandhar| 301543441 | hmk9@sfu.ca |
| Rohan Mathur | 301544232 | rma135@sfu.ca |

## Purpose & Motivation
Are you tired of attending concerts and feeling like you're not fully immersed in the experience? Do you struggle to discover live music events that truly align with your tastes and preferences? Look no further! Our project offers a personalized and improved concert discovery experience that will transform the way you enjoy live music.

Using cutting-edge machine learning algorithms, our platform analyzes your Spotify playlist and predicts your preferred music genre. This allows us to provide highly personalized and relevant concert recommendations that cater to your unique tastes. Whether you're a die-hard fan of indie rock, a lover of electronic beats, or anything in between, our system will ensure that you never miss out on a concert that's perfect for you.

But it's not just about enhancing your concert experience. By making it easier for you to discover and attend concerts that align with your interests, we're also helping you embark on a more fulfilling live music journey. Imagine discovering new artists and experiencing live performances that leave you feeling truly inspired and energized. That's the power of our personalized concert discovery platform.

## Overview: Spotify

Spotify is a digital music streaming platform that offers users access to millions of songs, podcasts, and other audio content from around the world. The service was launched in 2008 and has since become one of the most popular music streaming services in the world. Spotify offers both free and premium subscription options, with the latter providing additional features such as ad-free listening, offline playback, and higher-quality audio. Users can access Spotify via the web or through the Spotify app, which is available for download on various devices including smartphones, tablets, computers, and smart speakers. Additionally, Spotify offers a range of features such as personalized playlists, social sharing, and algorithmic music recommendations, which help users discover new music and connect with others who share their musical tastes.

## Overview: Ticketmaster

Ticketmaster is a global marketplace for buying and selling tickets to live events, including concerts, sports games, theater performances, and more. Founded in 1976, Ticketmaster has grown to become one of the largest ticketing companies in the world, providing access to events in over 30 countries. The company offers a range of services, including online ticket sales, mobile ticketing, and ticket resale. Through its website and app, Ticketmaster provides users with a convenient way to browse events, purchase tickets, and manage their bookings.

## Problem Definition

Our project aims to solve the lack of personalized and immersive concert experiences. Traditional methods of concert discovery often led to attendees feeling disconnected from the music and performers and struggling to find events that truly align with their musical preferences, especially in a new country or city. This can result in missed opportunities to discover new artists and enjoy live music to its fullest potential. Our platform utilizes machine learning algorithms to provide highly personalized and relevant concert recommendations based on a user's Spotify playlist and predicted music genre. By doing so, we aim to transform the way people experience live music and make it easier for them to embark on a more fulfilling live music journey.


## Prerequisites

- Python3
- Apache Spark
- AWS Connection Credentials
- Flask
- Spotify API Developer Credentials
- Ticketmaster API Developer Credentials


## Project Structure

```
.
├── __init__.py
├── README.md
└── src
    ├── application
    │   ├── analysis
    │   │   ├── __init__.py
    │   │   └── playlist_analysis.py
    │   ├── app.py
    │   ├── concerts
    │   │   ├── concert_extraction.py
    │   │   └── __init__.py
    │   ├── data
    │   │   └── __init__.py
    │   ├── feature_engineering
    │   │   ├── get_song_features.py
    │   │   ├── __init__.py
    │   │   └── test_playlist_to_csv.py
    │   ├── __init__.py
    │   ├── recommendation
    │   │   ├── __init__.py
    │   │   └── Spotify_ml_model_eval_2.py
    │   ├── requirements.txt
    │   ├── static
    │   │   └── __init__.py
    │   ├── templates
    │   │   ├── about.html
    │   │   ├── analyse.html
    │   │   ├── error.html
    │   │   ├── index.html
    │   │   ├── info.html
    │   │   ├── recomend.html
    │   │   └── showRecomendations.html
    │   └── utils
    │       └── __init__.py
    ├── commons
    │   ├── __init__.py
    │   └── spotify_api_functions.py
    ├── data
    │   ├── csv
    │   │   ├── clean_data
    │   │   │   └── clean_data.csv
    │   │   └── __init__.py
    │   ├── __init__.py
    │   ├── json
    │   │   ├── acoustic_1nq8tPEJPtRLIZ1DywckTx.json
    │   │   ├── acoustic_1URfoVZ0TuxvwulPDIuSfv.json
    │   │   ├── acoustic_1XqePqKyv638EBMhjpgYF9.json
    │   │   ├── acoustic_4Xv7w5RBLUz71sSzIs4C6b.json
    │   │   ├── acoustic_6vGKywnOyWTlYMluMmWF3Z.json
    │   │   └── __init__.py
    │   └── playlists
    │       ├── acoustic_playlists.txt
    │       ├── afrobeat_playlists.txt
    │       ├── alt-country_playlists.txt
    │       ├── alternatives_playlists.txt
    │       ├── ambient_playlists.txt
    │       └── __init__.py
    ├── machine_learning
    │   ├── __init__.py
    │   ├── Spotify_Genre_Classification_Models.ipynb
    │   ├── spotify_ml_eval_temp.py
    │   ├── spotify_ml_model_36.py
    │   └── spotify_ml_model_60.py
    ├── scraping
    │   ├── extract_s3_data.py
    │   ├── __init__.py
    │   ├── json_to_csv_processing.py
    │   ├── load_data.py
    │   ├── playlists_to_json.py
    │   └── scrape_playlists.py
    └── utils
        ├── get_song_features.py
        └── __init__.py

```

## Data Source

**Spotify Playlists**

 This dataset consists of at least 60 playlists from 93 different genres (each containing at least 50 songs) with various information on the songs. It was used to train the machine learning model, which was used to predict the genre of a user-given playlist based on the songs in the playlist. The dataset was scraped from the Spotify website using Spotify’s API and supporting Python libraries to ensure access to the latest information.


**Ticketmaster Data** 

This dataset gives information on concerts happening in the user-selected location during the given time period. It contains information such as the location, date and time of the concert, the artists performing, the venue, and the ticket price. The dataset is retrieved using the TicketMaster API which takes the predicted genre from the ML model to fetch the latest concerts.


**User Playlist** 

This dataset will contain data from the user input playlist, which will be retrieved using the Spotify API to fetch various information about the playlist. This data will then be used to analyze the user's music taste and predict the genre for the playlist to recommend concerts to the user.


## Approach to the Solution

Our project began by identifying various music genres present on Spotify worldwide. We then collected multiple playlists for each genre and utilized them to train our machine-learning model. This model predicts the top 5 genres based on a user's provided playlist, catering to their individual music preferences. The application uses this predicted genre to recommend concerts to users via the Ticketmaster API. Additionally, the user's playlist is analyzed and can be viewed by the user to gain a better understanding of their musical taste. 

**Data Scraping**

Data was scraped using Spotify's API. Scripts were written to accomodate different types of features of songs for extraction for a single playlist. Initially, script for scraping playlist information, which consisted of playlist IDs was written. This script defined 60 sub-genres, which were taken from the internet, and used these sub-genres to scrape 60 playlists for each genre. This gave out approximately **5,500** playlists, which contained numerous songs. 

After extracting playlist IDs for each genre, using these ID's, features for each song in these playlists were scraped using another script. Scraping for features of songs ran for approximately **3 days**, by shuffling API keys and gathering approximately **1.17GB** in data in JSON format.

After gathering features for each song for each playlist, a **PySpark** script was written to clean and preprocess the data entries, which resulted in a combined CSV of approximately **730,000** rows. This CSV will then be used for machine learning modelling.

Features of songs that were scraped are defined as below - 

- **Danceability** - Danceability describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity. A value of 0.0 is least danceable and 1.0 is most danceable.

- **Energy** - Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute include dynamic range, perceived loudness, timbre, onset rate, and general entropy.

- **Key** - The key the track is in. Integers map to pitches using standard Pitch Class notation. E.g. 0 = C, 1 = C#/Db, 2 = D, and so on.

- **Loudness** - The overall loudness of a track in decibels (dB). Loudness values are averaged across the entire track and are useful for comparing relative loudness of tracks. Loudness is the quality of a sound that is the primary psychological correlate of physical strength (amplitude). Values typical range between -60 and 0 db.

- **Mode** - Mode indicates the modality (major or minor) of a track, the type of scale from which its melodic content is derived. Major is represented by 1 and minor is 0.

- **Speechiness** - Speechiness detects the presence of spoken words in a track. The more exclusively speech-like the recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value. Values above 0.66 describe tracks that are probably made entirely of spoken words. Values between 0.33 and 0.66 describe tracks that may contain both music and speech, either in sections or layered, including such cases as rap music. Values below 0.33 most likely represent music and other non-speech-like tracks.

- **Acousticness** - A confidence measure from 0.0 to 1.0 of whether the track is acoustic. 1.0 represents high confidence the track is acoustic.

- **Instrumentalness** - Predicts whether a track contains no vocals. "Ooh" and "aah" sounds are treated as instrumental in this context. Rap or spoken word tracks are clearly "vocal". The closer the instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content. Values above 0.5 are intended to represent instrumental tracks, but confidence is higher as the value approaches 1.0.

- **Liveness** - Detects the presence of an audience in the recording. Higher liveness values represent an increased probability that the track was performed live. A value above 0.8 provides strong likelihood that the track is live.

- **Valence** - A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry).

- **Tempo** - The overall estimated tempo of a track in beats per minute (BPM). In musical terminology, tempo is the speed or pace of a given piece and derives directly from the average beat duration.

**Analysis**

After the user provides the link to their playlist, the application extracts all songs and associated information from the playlist. This data is pre-processed before analysis, which is then utilized to generate various graphs and information about the user's playlist. The generated information includes playlist uniqueness, playlist length, popularity, and graphs showing danceability, happiness, top genres, and top artists. This information is then displayed on the application for the user to view and gain insights into their musical taste.  

**Machine Learning Models & Training**

This section outlines three different approaches for predicting the genre of music tracks on Spotify using ***NLP Lemmatization*** and ***Bag of Words*** techniques. The first approach involves consolidating the list of genres for each track using lemmatization, resulting in an accuracy of 36%. The second approach utilizes a Bag of Words technique to consolidate the genre list, resulting in an accuracy of 60% but only on the 17 genres available on both Spotify and Ticketmaster. As a final approach, to improve accuracy, a ***Voting Ensemble Model*** is developed that combines the predictions of both models. The final model is used to recommend music concerts to users based on their playlist as well as time and location preferences. 


**Application**

The web application is built using Flask and Requests for the backend. Webpages are created using HTML, Jinja2, and CSS for styling. Upon loading the home page, the user is prompted to input the link to their playlist. This link is utilized to extract song data and related information, which is then stored as a CSV file in the data folder. The application offers two options to the user: Analysis and Recommendation. If the Analysis option is selected, the user is redirected to a new page where they can view all analytics generated from their playlist. If the Recommendation option is selected, the user is redirected to a new page where the top 5 predicted genres are displayed, and the user is prompted to provide additional information such as their preferred location and time range for concert recommendations. This information, combined with the predicted genre, is used to generate personalized concert recommendations for the user, which are then displayed on a new page. The web application is hosted using EC2.

## Results

- The project provided the team with a comprehensive understanding of the evolution of music over the years and the emergence of different genres. Through the analysis of Spotify data, the team discovered that many new genres are sub-genres of existing ones.

- To develop a more accurate model, the team combined two machine learning models with an ensemble approach. The analysis of playlists provided insights into the music preferences of various individuals, which helped in refining the models.

- Working with APIs from Spotify and Ticketmaster provided the team with practical experience in extracting various information. The project allowed the team to use different technologies like Flask and Request to create a web application for a better user experience.

- The team learned Agile Methodologies and the Software Development Lifecycle, including initial architecture design and code structures. Agile allowed the team to easily adjust to changing requirements, which was not possible in the waterfall model.

- Overall, the project proved to be a valuable learning opportunity for the team, providing them with a practical understanding of music analysis, machine learning, API usage, web application development, and Agile methodologies.


## Project Execution

Please [CLICK HERE](http://ec2-52-32-239-227.us-west-2.compute.amazonaws.com:5000/)

We have hosted the project on an AWS EC2 instance to make it more convenient for you. You don't need to set up anything on your local machine. All you need to do is click on the [link](http://ec2-52-32-239-227.us-west-2.compute.amazonaws.com:5000/) we've provided and start playing around with the website!

We have tried our best to make everything work smoothly, but if you encounter any issues or glitches, don't worry! Just refresh the page and start from the homepage. We hope you enjoy exploring our project.


## Summary

- The project provided the team with an opportunity to explore the vastness of big data and solve real-world problems while learning and applying big data applications. 

- Large data sets allowed for the uncovering of hidden patterns, unknown correlations, and user preferences, providing valuable information that enhanced the user experience and helped to solve real-world problems.

- The project provided the team with practical experience in data science. By leveraging data-driven insights, the team was able to make informed decisions and implement effective solutions to address the problem at hand.

- The team gained a practical understanding of the Software Development Lifecycle and valuable experience in dealing with interesting challenges as a result of the project.

---

Thank you!
