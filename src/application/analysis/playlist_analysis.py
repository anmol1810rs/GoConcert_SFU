'''
This file contains the code to analyze the playlist and generate the radar chart and the relationship plots

Input: playlist_data.csv

Output: radar_chart.html, relationship_plots.html

usage: python playlist_analysis.py playlist_data.csv

'''


import numpy as np
import pandas as pd
import matplotlib.pyplot as plot
import seaborn as sns
import pygal
import plotly.graph_objs as go
import plotly.io as pio
import re
import plotly.express as px
from jinja2 import Template




# Define a function to convert loudness values to a 0-100 scale
def loudness_norm(loudness, min_l, max_l):

  '''
    Function to normalize loudness values to a 0-100 scale

    Args:

        param1 (float): loudness value
        param2 (float): minimum loudness value
        param3 (float): maximum loudness value
    
    Returns:

        float: returns normalized loudness value
  '''  

  #Applying the min max scaler formula
  l_min = min_l
  l_max = max_l
  return float((loudness - l_min)/(l_max - l_min)*100)

def tempo_norm(tempo, min_tempo, max_tempo):

  '''
    Function to normalize tempo values to a 0-100 scale

    Args:

        param1 (float): tempo value
        param2 (float): minimum tempo value
        param3 (float): maximum tempo value

    Returns:

        float: returns normalized tempo value
  '''  

  #Applying the min max scaler formula
  t_min = min_tempo
  t_max = max_tempo
  return float((tempo - t_min)/(t_max - t_min)*100)


def preprocess_playlist(song_df):

    '''
    Function to preprocess the playlist data

    Args:

        param1 (dataframe): dataframe containing the playlist data

    Returns:

        dataframe: returns the preprocessed dataframe
    '''


    song_df = song_df.dropna(how='any')

    # preprocessing the data
    song_df['acousticness'] = song_df['acousticness'].apply(lambda x: 100*x)
    song_df['danceability'] = song_df['danceability'].apply(lambda x: 100*x)
    song_df['energy'] = song_df['energy'].apply(lambda x: 100*x)
    song_df['instrumentalness'] = song_df['instrumentalness'].apply(lambda x: 100*x)
    song_df['liveness'] = song_df['liveness'].apply(lambda x: 100*x)
    song_df['speechiness'] = song_df['speechiness'].apply(lambda x: 100*x)
    song_df['valence'] = song_df['valence'].apply(lambda x: 100*x)


    max_loudness = song_df['loudness'].max()
    min_loudness = song_df['loudness'].min()
    song_df['loudness'] = song_df['loudness'].apply(lambda x: loudness_norm(x, min_loudness, max_loudness))

    max_temp = song_df['tempo'].max()
    min_temp = song_df['tempo'].min()
    song_df["tempo"] = song_df['tempo'].apply(lambda x: tempo_norm(x, min_temp, max_temp))

    # return the preprocessed data
    return song_df



def create_spider(data):

    '''
    Function to create the radar chart

    Args:

        param1 (dataframe): dataframe containing the playlist data

    output:

        radar_chart.svg: creates and saves the radar chart
    '''

    song_df = data

    # Define the audio features to include in the radar chart
    audio_features = ["acousticness", "danceability", "energy",  "liveness", "loudness", "speechiness", "tempo", "valence"]
    #"instrumentalness",
    # Create a radar chart
    radar_chart = pygal.Radar(width=600, height=350,fill=True, range=(0,100))
    radar_chart.title = 'Audio Features of Playlist Songs'
    radar_chart.x_labels = audio_features

    # Iterate over the top 10 songs and add their audio feature values to the chart
    for i in range(len(song_df)):
        # Get the audio feature values for the song
        values = [song_df.iloc[i][col] for col in audio_features]
    
        # Add the values to the chart
        radar_chart.add(song_df.iloc[i]['name'], values)

    # Save the chart to an SVG file
    radar_chart.render_to_file('static/songs_radar_chart.svg')

def relationship_plot(data):

    '''
    Function to create the relationship plots

    Args:

        param1 (dataframe): dataframe containing the playlist data

    output:

        relationship_plots.html: creates and saves the relationship plots

    '''
    


    song_df = data

    # Create a scatter plot of the tempo, valance and energy features
    fig = go.Figure(data=[go.Scatter3d(
        x=song_df['tempo'],
        y=song_df['energy'],
        z=song_df['valence'],
        mode='markers',
        marker=dict(
            size=5,
            color=song_df['valence'],
            colorscale=[(0, 'blue'), (0.5, 'white'), (1, 'red')],
            opacity=0.8,
            colorbar=dict(
                title='Valence Feature Scatter'
            )
        )
    )])

    fig.update_layout(
        scene=dict(
            xaxis_title='Tempo (BPM)',
            yaxis_title='Energy',
            zaxis_title='Valence'
        ),
        xaxis_title="Tempo (BPM)",
        yaxis_title="Energy",
        legend_title="",
        title={
            'text': "How Happy is your PlayList ?",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )

    # Save the plot to an HTML file
    pio.write_html(fig, 'static/relationship_plot.html')

def top_artist(song_df):

    '''
    Function to create the top 5 artists bar chart

    Args:

        param1 (dataframe): dataframe containing the playlist data

    output:

        top_artists.html: creates and saves the top 5 artists bar chart

    '''

    artist_name = []
    for ars in song_df['artists']:
        names = re.split(r',\s*|,', ars)
        for val in names:
            artist_name.append(str(val))

    name_df = pd.DataFrame(artist_name)
    name_df = name_df.rename(columns = {0:'Artist'})

    # Count  of the top 5 occurrences of each value in the 'Fruit' column
    name_df['Artist'] = name_df['Artist'].apply(lambda x: x.title())

    counts = name_df['Artist'].value_counts()
    # Filter the counts to only include values with count more than two
    counts_filtered = counts.nlargest(5)
    # Create a bar chart of the filtered counts using plotly
    colors = px.colors.qualitative.Pastel

    # Create a bar chart to show top 5 artists
    fig = px.bar(counts_filtered,
                x=counts_filtered.index,
                y=counts_filtered.values,
                color = counts_filtered.values,
                color_discrete_sequence=colors, 
                labels={'x': 'Genre', 'y': 'Number of Songs'})

    # Update the layout of the plot
    fig.update_layout(
        xaxis_title='Top Artists',
        yaxis_title='Song Count',
        title={
            'text': 'The Fab Five: A Musical Journey through Your Top 5 Artists',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        legend_title='Legend',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # Save the plot to an HTML file
    pio.write_html(fig, 'static/top_artist_plot.html')
    return counts_filtered

def genre_analysis(data):

    ''' 
    Function to create the top 5 genres pie chart

    Args:

        param1 (dataframe): dataframe containing the playlist data

    output:

        top_genres.html: creates and saves the top 5 genres pie chart

    '''

    
    song_df = data
    genres = []

    # Split the genres and add them to a list
    for ars in song_df['artist_genre']:
        names= re.split(r',\s*|,', ars)
        for val in names:
            if val=="":
                continue
            genres.append(str(val))

    genre_df = pd.DataFrame(genres)
    genre_df = genre_df.rename(columns = {0:'Genre'})

    # Count  of the top 5 occurrences of each genre in the 'Genre' column
    genre_df['Genre'] = genre_df['Genre'].apply(lambda x: x.title())
    counts = genre_df['Genre'].value_counts().nlargest(5)

    # Create a pie chart of the filtered counts using plotly
    fig = go.Figure(data=[go.Pie(
        labels=counts.index,
        values=counts.values,
        hole=0.3,
        pull=[0.1, 0, 0, 0, 0],
        marker=dict(colors=px.colors.qualitative.Plotly)
    )])

    # Customize the chart layout
    fig.update_layout(
        title={
            'text': 'Top 5 Genres in your Playlist',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        font=dict(
            family='Arial',
            size=12,
            color='#7f7f7f'
        ),
        legend_title='Genres',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )

    )

    # Save the plot to an HTML file
    pio.write_html(fig, 'static/top_genre_analysis.html')

def calculate_uniqueness(data):

    ''' 
    Function to calculate the uniqueness of the playlist

    Args:

        param1 (dataframe): dataframe containing the playlist data

    output:
    
            uniqueness: returns the uniqueness of the playlist
    
    '''

    # load the song_df dataframe
    song_df  = data

    #Calculate the average popularity
    avg_popularity = song_df['popularity'].mean()

    #Calculate the average popularity of the 10 songs with the lowest popularity
    lowest_popularity = song_df.nsmallest(10, 'popularity')
    avg_popularity_lowest = lowest_popularity['popularity'].mean()

    # Compare the distribution of avg_popularity with respect to avg_popularity_lowest
    # Calculate the percentage uniqueness of the songs in the playlist
    uniqueness = ((avg_popularity - avg_popularity_lowest) / avg_popularity) * 100
    uniqueness = int(round(uniqueness,0))

    # Calculate the uniqueness of the playlist
    avg_popularity = song_df['popularity'].mean()
    lowest_popularity = song_df.nsmallest(10, 'popularity')
    avg_popularity_lowest = lowest_popularity['popularity'].mean()
    uniqueness = ((avg_popularity - avg_popularity_lowest) / avg_popularity) * 100
    uniqueness = int(round(uniqueness,0))

    # Return the uniqueness of the playlist
    return uniqueness

def create_bins(data):

    '''
    Function to create bins for the audio features

    Args:

        param1 (dataframe): dataframe containing the playlist data

    output:

        bins: returns the bins for the audio features

    '''

    song_df = data
    
    # set the audio features to plot (take only dance, energy, loudness)
    audio_features = ["danceability", "energy", "loudness", "liveness"]
    color_sequence = px.colors.sequential.Plasma

    # create a histogram for each audio feature
    for i, feature in enumerate(audio_features):

        # Create a histogram to show the distribution of the audio feature
        fig = px.histogram(song_df,
                        x=feature,
                        nbins=20,
                        title=feature.capitalize(),
                        labels={feature: feature.capitalize(),"count": "Number of Songs"},
                        color_discrete_sequence=[color_sequence[i]])

        # Update the layout of the plot
        fig.update_layout(
        xaxis_title= f"{feature.capitalize()} Feature",
        yaxis_title="Count of Playlist Songs",
        legend_title="Legend Title",
        title={
            'text': f"{feature.capitalize()} Distribution of the User's Playlist",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'}
        )
        file_name = "static/"+feature+"_bin.html"

        # Save the plot to an HTML file
        pio.write_html(fig, file_name)

def feature_year_comparision(data):

    ''' 
    Function to create the line plots for the audio features

    Args:

        param1 (dataframe): dataframe containing the playlist data

    output:

        audio_features.html: creates and saves the line plots for the audio features

    '''


    song_df = data

    #Checking how valence has changed over the years (higher velance represtns a happier emotional quotient of the song)
    #group by year and take the mean of valence for each year (popularity, energy, tempo, loudness)
    audio_features = ["energy", "tempo", "valence", "loudness", "popularity"]

    # Create a line plot for each audio feature
    for feature in audio_features:
        feature_by_year = song_df.groupby('album_release_date')[feature].mean()

        # Create a line plot to show the distribution of the audio feature
        fig = px.line(
            feature_by_year, 
            title=feature.capitalize() + 'Distribution By Release Year', 
            labels={'album_release_date':'Year of Song Release', 
            feature: feature.capitalize()
            })
        
        # Update the layout of the plot
        fig.update_layout(
            xaxis_title='Song Release Year',
            yaxis_title=feature.capitalize(),
            title={
                'text': feature.capitalize() + ' Distribution By Release Year',
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            legend_title='Legend',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        # Save the plot to an HTML file
        file_name = "static/"+feature+"_by_year.html"

        # Save the plot to an HTML file
        pio.write_html(fig, file_name)


def top_artist_sentiment(data, counts):

    '''
    Function to create the bar plots for the top 5 artists

    Args:

        param1 (dataframe): dataframe containing the playlist data

    output:

        top_artist_sentiment.html: creates and saves the bar plots for the top 5 artists

    '''

    # load the song_df dataframe
    counts_filtered = counts
    song_df = data

    # Get the top 5 artists in the playlist
    top5_artists = counts_filtered.index.tolist()
    
    # Convert the artist names to lowercase
    for i in range(0,len(top5_artists)):
        top5_artists[i] = top5_artists[i].lower()

    # Create a dataframe with the top 5 artists
    top5_df = song_df.head(5)
    top5_df.drop(top5_df.index, inplace=True)

    for artist in top5_artists:
        temp_df = song_df[song_df['artists'].str.contains(artist)]
        temp_df['artists'] = artist
        top5_df = top5_df.append(temp_df)


    audio_features = ["acousticness", "energy", "tempo", "valence", "popularity"]

    top5_df['artists'] = top5_df['artists'].apply(lambda x: x.title())

    #Features to be taken: - Popularity,  Valence, Instrumentalness
    for feature in audio_features:

        # Create a box plot to show the distribution of the audio feature
        fig = px.box(
            top5_df, 
            x='artists', 
            y=feature, 
            color='artists', 
            title = feature.capitalize() + ' Distribution by Artist'
            )

        # Update the layout of the plot
        fig.update_layout(
            xaxis_title='Artists', 
            yaxis_title=feature.capitalize(),
            title={
                'text': feature.capitalize() + ' Distribution by Artist',
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }, 
            legend_title='Artists',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
            )
        
        # Save the plot to an HTML file
        file_name = "static/"+feature+"_of_artist.html"
        pio.write_html(fig, file_name)
        
def get_playlist_feature(song_df):

    '''
    
    Function to get the playlist features
    
    Args:
    
        param1 (dataframe): dataframe containing the playlist data
        
    output:
        
        playlist_features.html: creates and saves the bar plots for the top 5 artists
        
    '''

    total_songs = len(song_df)

    #Average Popularity
    avg_popularity = song_df['popularity'].mean()
    avg_popularity = np.round(avg_popularity, 2)

    #Most Listened Year
    song_df['album_release_date'] = song_df['album_release_date'].apply(lambda x: int(x))
    most_listened_year = song_df['album_release_date'].value_counts().nlargest(1)
    most_listened_year = most_listened_year.index.tolist()[0]

    #Most Listened Decade
    song_df['decade'] = np.round(song_df['album_release_date'] / 10) * 10
    most_listened_decade = song_df['decade'].value_counts().nlargest(1)
    most_listened_decade = most_listened_decade.index.tolist()[0]
    most_listened_decade = str(int(most_listened_decade)) +"s"

    #Most Popular Track
    most_popular_track = song_df.loc[song_df['popularity'] == song_df['popularity'].max(), 'name'].tolist()[0]
    most_popular_track = most_popular_track.title()

    #Total Duration
    total_playlist_duration = (song_df['duration_ms'].sum()) / (1000 * 60)
    total_playlist_duration = np.round(total_playlist_duration, 2)

    #Average Track Duration
    avg_track_duration = (song_df['duration_ms'].mean()) / (1000*60)
    avg_track_duration = np.round(avg_track_duration, 2)

    #Convert to string
    total_playlist_duration = str(total_playlist_duration) + " minutes"
    avg_track_duration = str(avg_track_duration) + " minutes"

    #Create a list of all the features
    feature_array = [total_songs, avg_popularity, most_listened_year, most_listened_decade, most_popular_track, total_playlist_duration, avg_track_duration]
    
    #Return the list of features
    return feature_array


def create_graphs(file_name):

    ''' 
    Function to create all the graphs for the playlist

    Args:

        param1 (string): name of the csv file containing the playlist data

    output:

        Creates various graphs for the playlist and returns a list of features from the playlist
    
    '''

    # Read the csv file
    song = pd.read_csv(file_name)

    # Preprocess the data in the dataframe
    song_df = preprocess_playlist(song)


    # Create the spider plot
    create_spider(song_df)
    print("1 done")

    # Create the relationship plot
    relationship_plot(song_df)
    print("2 done")

    # Create the top artist plot
    counts_filtered = top_artist(song_df)
    print("3 done")

    # Create the genre plot
    genre_analysis(song_df)
    print("4 done")

    # Get the uniqueness of the playlist
    uniqueness = calculate_uniqueness(song_df)
    print("5 done")

    # Create the audio feature plots
    create_bins(song_df)
    print("6 done")

    # Create the audio feature plots
    feature_year_comparision(song_df)
    print("7 done")

    # Create the audio feature plots
    top_artist_sentiment(song_df,counts_filtered)
    print("8 done")

    # Get the playlist features
    features = get_playlist_feature(song_df)

    # Append the uniqueness to the list of features
    features.append(uniqueness)

    print("All done")

    # Return the list of features
    return features
