# Here you can add any global configurations
import pandas as pd

path = "../data/"
# Update the paths below to match the location of the files on your machine
ratings = pd.read_csv("../data/ratings.csv")
tags = pd.read_csv("../data/tags.csv")
movies = pd.read_csv("../data/movies.csv")
links = pd.read_csv("../data/links.csv")

# Preview the data
print("Ratings:")
print(ratings.head(), "\n")

print("Tags:")
print(tags.head(), "\n")

print("Movies:")
print(movies.head(), "\n")

print("Links:")
print(links.head())
