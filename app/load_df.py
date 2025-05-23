import pandas as pd
import os
import re

"""Never use these global dataframes directly
If you want to modify them make a new dataframe 
(e.g. df = users_df) and use that instead"""


# Individual dataframes loaded directly from file
users_df = pd.read_csv(
    'data/ml-1m/users.dat',
    sep='::',
    engine='python',
    names=['UserID', 'Gender', 'Age', 'Occupation', 'Zip-code']
)

movies_df = pd.read_csv(
    'data/ml-1m/movies.dat',
    sep='::',
    engine='python',
    names=['MovieID', 'Title', 'Genres'],
	encoding='latin-1'
)

ratings_df = pd.read_csv(
    'data/ml-1m/ratings.dat',
    sep='::',
    engine='python',
    names=['UserID', 'MovieID', 'Rating', 'Timestamp'],
	encoding='latin-1'
)

ratings_df['Timestamp'] = pd.to_datetime(ratings_df['Timestamp'], unit='s')


# Merged dataframes
ratings_movies = pd.merge(ratings_df, movies_df, on='MovieID', how='left')
full_df = pd.merge(ratings_movies, users_df, on='UserID', how='left')
full_df['Year'] = full_df['Title'].str.extract(r'\((\d{4})\)').astype(float)

# Unique genres
genre_lists = full_df['Genres'].str.split('|')
all_genres = [genre for sublist in genre_lists for genre in sublist]
unique_genres = sorted(set(all_genres))