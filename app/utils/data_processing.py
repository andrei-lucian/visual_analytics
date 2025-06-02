import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pandas as pd
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import pickle
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler

# Read data frame
data_df = pd.read_csv("data/movielens_32m_omdb_with_description.csv")

# Add primary genre for colouring purposes
data_df["PrimaryGenre"] = data_df["Genre"].str.split(",").str[0]


# PCA dimensionality reduction
with open("data/32m_pca_scaled.pkl", "rb") as f:
    scaled_reduced = pickle.load(f)

data_df["pca_x"] = scaled_reduced[:, 0]
data_df["pca_y"] = scaled_reduced[:, 1]


# Unique genres
genre_series = data_df["Genre"].dropna().apply(lambda x: [genre.strip() for genre in x.split(",")])
all_genres = [genre for sublist in genre_series for genre in sublist]
unique_genres = sorted(set(all_genres))


# Number of movies per year
df_stream = data_df.copy()
df_stream["GenreList"] = df_stream["Genre"].str.split(", ")
df_stream = df_stream.explode("GenreList")
genre_year_counts = (
    df_stream.groupby(["Year", "GenreList"]).size().reset_index(name="Count").sort_values(["Year", "GenreList"])
)
genre_pivot = genre_year_counts.pivot(index="Year", columns="GenreList", values="Count").fillna(0)


# Average movie rating per year
df_line = data_df.copy()
df_line["GenreList"] = df_line["Genre"].str.split(", ")
df_line = df_line.explode("GenreList")
genre_year_avg_rating = df_line.groupby(["Year", "GenreList"])["imdbRating"].mean().reset_index()
