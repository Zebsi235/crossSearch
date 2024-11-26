import os
# Configuration file for the app

PROWLARR_API_URL = os.getenv("URL_PROWLARR", "http://192.168.0.10:9696")
TMDB_API_KEY = os.getenv("API_KEY_TMDB", "") # Replace with your TMDb API key
API_KEY_PROWLARR = os.getenv("API_KEY_PROWLARR", "") 
API_KEY_OMDB = os.getenv("API_KEY_OMDB", "") 
TOP_TORRENTS_LIMIT = 5
TORRENTS_LIMIT = 100
DEBUG_REFRESH = False

TMDB_API_URL = "https://api.themoviedb.org/3"


# movie / tv
SEARCH_CATEGORY= "movie"
