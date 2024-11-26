import sqlite3
import requests
import json
from config import *
import os
import streamlit as st # Debug only


####################################
# File/DB Handeling
####################################
def is_file_empty(filename):
    """
    Check if a file exists and whether it is empty or not.
    
    Parameters:
    - filename (str): The name of the file to check.
    
    Returns:
    - bool: True if the file exists and is empty, False otherwise.
    """
    if not os.path.exists(filename):
        #print(f"File '{filename}' does not exist.")
        return True  # Treat non-existent files as empty
    if os.path.getsize(filename) == 0:
        #print(f"File '{filename}' is empty.")
        return True  # File exists but has no content
    ##print(f"File '{filename}' is not empty.")
    return False

def save_titles_to_file(titles, filename="titles.txt"):
    """
    Save a list of titles to a text file, one title per line.
    
    Parameters:
    - titles (list): List of titles to save.
    - filename (str): Name of the text file (default: 'titles.txt').
    """
    with open(filename, "w", encoding="utf-8") as file:
        for title in titles:
            file.write(title + "\n")
    #print(f"Titles successfully saved to {filename}")


def read_titles_from_file(filename="titles.txt"):
    if not os.path.exists(filename):
        raise FileNotFoundError(f"The file {filename} does not exist.")
    with open(filename, "r", encoding="utf-8") as file:
        titles = [line.strip() for line in file]
    #print(f"Titles successfully read from {filename}")
    return titles

# Initialize SQLite Database
def initialize_database():
    """
    Create the torrents table if it doesn't already exist.
    """
    conn = sqlite3.connect("torrents.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS torrents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            info_hash TEXT UNIQUE,
            name TEXT,
            size INTEGER,
            added_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


# Save Torrents to Database
def save_torrents_to_db(torrents):
    """
    Save torrents to the SQLite database, ignoring duplicates.
    """
    conn = sqlite3.connect("torrents.db")
    cursor = conn.cursor()
    for torrent in torrents:
        try:
            cursor.execute(
                """
                INSERT OR IGNORE INTO torrents (info_hash, name, size)
                VALUES (?, ?, ?)
                """,
                (torrent["infoHash"], torrent["title"], torrent["size"]),
            )
        except KeyError:
            pass  # Ignore torrents without required fields
    conn.commit()
    conn.close()


####################################
# OMDB Top list
####################################
def get_top_titles_titles(limit, api_key=API_KEY_OMDB):
    """
    Fetch the top 100 movie titles from OMDb API.
    The API does not directly provide a "Top 100" endpoint, so this function fetches movies by popular years and genres.
    
    Args:
        api_key (str): Your OMDb API key.
    
    Returns:
        list: A list of dictionaries containing movie titles and years.
    """
    base_url = "http://www.omdbapi.com/"
    search_years = [2020, 2021, 2022, 2023]  # Popular years for recent movies
    search_terms = ["popular", "top", "blockbuster", "hit"]  # Broad search terms
    results = []

    for year in search_years:
        for term in search_terms:
            params = {
                "apikey": api_key,
                "s": term,  # Search term
                "type": SEARCH_CATEGORY,  # Filter for movies
                "y": year,  # Filter by year
            }
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if "Search" in data:
                    for movie in data["Search"]:
                        if len(results) < limit:
                            results.append({"Title": movie["Title"], "Year": movie["Year"]})
                        else:
                            #print(f"results:{results}")
                            return results
            #else:
                #print(f"Error fetching data for year {year} and term '{term}': {response.status_code}")
                #print(response.text)
    
    #print(f"results:{results}")
    return results

####################################
# TMDB Top list movies
####################################
def get_top_titles(limit):
    """
    Fetch the top 100 popular movie titles from The Movie Database (TMDb).
    """
    top_movies = []
    page = 1

    while len(top_movies) < limit:
        # Make the API request for the popular movies
        response = requests.get(
            f"{TMDB_API_URL}/{SEARCH_CATEGORY}/popular",
            params={
                "api_key": TMDB_API_KEY,
                "language": "en-US",
                "page": page
            },
        )
        response.raise_for_status()
        data = response.json()

        # Extract movie titles
        movies = data.get("results", [])
        #print("Tester")
        for movie in movies:
            top_movies.append(movie["title"])
            if len(top_movies) >= limit:
                break

        # Increment the page to fetch the next batch of movies
        page += 1
        if page > data["total_pages"]:  # Stop if there are no more pages
            break

    return top_movies

####################################
# TMDB Top list series
####################################
def get_top_titles_series(limit):
    """
    Fetch the top 100 popular TV series titles from The Movie Database (TMDb).
    
    Returns:
    - list: A list of the top 100 popular TV series titles.
    """
    top_series = []
    page = 1

    while len(top_series) < limit:
        # Make the API request for the popular TV series
        response = requests.get(
            f"{TMDB_API_URL}/tv/popular",
            params={
                "api_key": TMDB_API_KEY,
                "language": "en-US",
                "page": page
            },
        )
        response.raise_for_status()
        data = response.json()

        # Extract TV series titles
        series = data.get("results", [])
        for tv in series:
            top_series.append(tv["name"])  # TV series titles are under the 'name' field
            if len(top_series) >= limit:
                break

        # Increment the page to fetch the next batch of series
        page += 1
        if page > data["total_pages"]:  # Stop if there are no more pages
            break

    return top_series

def generateTopTitleList(limit, save_file):
    top_titles = None
    ##print("Yeet")
    if SEARCH_CATEGORY == "movie":
        top_titles = get_top_titles(limit)
        #print("got top movies")
    elif SEARCH_CATEGORY == "tv":
        top_titles = get_top_titles_series(limit)
        #print("got top series")

    if save_file:
        if top_titles != None:
            save_titles_to_file(top_titles, filename=f"{SEARCH_CATEGORY}.txt")
        #else:
            #print("Fuck")
    elif not is_file_empty(f"{SEARCH_CATEGORY}.txt") and DEBUG_REFRESH:
        top_titles = read_titles_from_file(filename=f"{SEARCH_CATEGORY}.txt")

    return top_titles


####################################
# Prowlarr api requests
####################################

def fetch_trackers():
    try:
        headers = {"X-Api-Key": API_KEY_PROWLARR}
        response = requests.get(f"{PROWLARR_API_URL}/indexer", headers=headers)
        response.raise_for_status() 
        return response.json()
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch trackers: {e}")
        #return []

# Request one title, multiple indexers at once
def fetch_torrents_multi(indexer_ids, limit=TORRENTS_LIMIT , title="a", category=None, search_type="search"):
    """
    Fetch torrents from a specific tracker with optional title and category parameters.
    """
    indexer_formated =  indexer_ids if isinstance(indexer_ids, list) else [indexer_ids]

    headers = {"X-Api-Key": API_KEY_PROWLARR}
    params = {
    "query": title, 
    "indexerIds": indexer_formated,
    "type": search_type,  # Type of search (search, tv, movie, etc.)
}

    if category:
        params["categories"] = ",".join(map(str, category)) if isinstance(category, list) else str(category)

    # Make the request
    response = requests.get(f"{PROWLARR_API_URL}/search", headers=headers, params=params)
    response.raise_for_status()
    return response.json()

# Fetch Torrents from API
def fetch_torrents(indexer_id, limit=TORRENTS_LIMIT , title="test", category=None, search_type="search"):
    """
    Fetch torrents from a specific tracker with optional title and category parameters.
    """
    headers = {"X-Api-Key": API_KEY_PROWLARR}
    params = {
        "indexerIds": indexer_id,
        "limit": limit, 
        "type": search_type,  # Type of search (search, tvsearch, moviesearch, etc.)
    }

    # Add dynamic query (title) if provided
    if title:
        params["query"] = title

    # Add categories as a comma-separated string if provided
    if category:
        if isinstance(category, list):
            params["categories"] = ",".join(map(str, category))  # Convert list to comma-separated string
        else:
            params["categories"] = str(category)
    # Make the request
    response = requests.get(f"{PROWLARR_API_URL}/search", headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def fetch_and_save_all_torrents( top_titles, indexer_list=[],indexer_id=-1, progress_callback=None):
    ##print("fetch and save Start")
    """
    Fetch all torrents from a tracker in batches, save them to the database,
    and update the progress using the callback.
    """
    initialize_database()  # Ensure the database is initialized
    
    torrents = []
    title_idx = 0

    while title_idx < len(top_titles):
        
        if indexer_id == -1 and indexer_list != []:
            batch = fetch_torrents_multi(indexer_list, title=top_titles[title_idx])
        else:
             # Fetch a batch of torrents
            batch = fetch_torrents(indexer_id, title=top_titles[title_idx])
        
        # Save new torrents to the database
        if batch:
            save_torrents_to_db(batch)
            torrents.extend(batch)

        title_idx += 1

        # Update progress
        if progress_callback:
            progress_callback(title_idx / len(top_titles))  # Scale progress to 100%
        

    return torrents
