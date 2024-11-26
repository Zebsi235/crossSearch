import streamlit as st
import pandas as pd
from api import fetch_and_save_all_torrents, fetch_trackers, generateTopTitleList, fetch_torrents_multi
from compare import compare_torrents
from config import API_KEY_OMDB, TMDB_API_KEY

from collections import defaultdict


if "u_input" not in st.session_state:
    st.session_state.u_input = ""
if "save_file" not in st.session_state:
    st.session_state.save_file = False
if "top_torrents_limit" not in st.session_state:
    st.session_state.top_torrents_limit = 10
if "show_all_torrents" not in st.session_state:
    st.session_state.show_all_torrents = False


# Fetch tracker names
tracker_names = fetch_trackers()

page = st.sidebar.selectbox("Choose a page:", ["Compare Top", "Search", "Tracker"])
# User Inputs
st.sidebar.header("Tracker Settings")
st.session_state.top_torrents_limit = st.empty()

# This can enable the ability to save the top list to a txt file. 
# Also watch config.py & DEBUG_REFRESH 
#st.session_state.save_file = st.sidebar.checkbox("Save Top")

st.session_state.show_all_torrents = st.sidebar.checkbox("Show all fetched torrents")

# Allow users to add tracker IDs dynamically
st.sidebar.write("Enter tracker IDs (0 = not used):")
num_trackers = st.sidebar.number_input("Number of Trackers", min_value=2, value=2)
trackers = []
for i in range(num_trackers):
    trackers.append(st.sidebar.number_input(f"Tracker {i + 1} ID", min_value=0, key=f"tracker_{i}"))

# Prints Matches in a "Table"
def showMatches(matches):
    st.success(f"Found {len(matches)} identical torrents!")
    matches = sorted(matches, key=lambda match: len(match['indexers']), reverse=True)
    for match in matches:
        with st.container():
            # Use columns to organize the display
            col1, col2 = st.columns([2, 1])
            
            # Display basic torrent info in the first column
            with col1:
                st.markdown(f"### {match['title']}")
                st.markdown(f"- **Size:** {match['size']} bytes")
            
            # Display tracker information in the second column
            with col2:
                st.markdown(f"#### Indexers")
                st.markdown(f"Found on **{len(match['indexers'])} indexers**:")
                st.write(", ".join(match['indexers']))

            # Divider for better readability
            st.divider()

def showTorrents(torrents):
    grouped_torrents = defaultdict(list)

    # Group torrents by their indexer
    for torrent in torrents:
        grouped_torrents[torrent['indexer']].append(torrent)

    # Display torrents grouped by indexer
    for indexer, torrents in grouped_torrents.items():
        st.subheader(f"Torrents from {indexer}")
        if torrents:
            # Ensure `torrents` is a list (this is already handled by defaultdict)
            tracker_df = pd.DataFrame(
                [{"Title": t["title"], "Size": t["size"], "Tracker": t["indexer"]} for t in torrents]
            )
            st.table(tracker_df)
        else:
            st.warning(f"No torrents found for {indexer}.")

######################################################
# APP
######################################################

#################### Compare #########################
if page == "Compare Top":
    st.title("Compare Top X Torrents") 
    st.session_state.top_torrents_limit = st.number_input("Number of Tops to fetch",min_value=1, value=25)
    
    if st.button("Compare"):
        if TMDB_API_KEY == "":
            st.error("Please provide a TMDB API KEY")
        else:
            try:
                # Initialize progress bar and status
                progress_bar = st.progress(0)

                status_text = st.empty()

                #all_torrents = []
                torrents = []

                progress_step = (1 / st.session_state.top_torrents_limit*len(trackers))

                st.write(f"Searching Top {st.session_state.top_torrents_limit} torrents on {len(trackers)} trackers")
                top_title_list = generateTopTitleList(st.session_state.top_torrents_limit ,st.session_state.save_file)

                torrents = fetch_and_save_all_torrents(top_title_list, indexer_list=[tracker_id for i, tracker_id in enumerate(trackers)], progress_callback=lambda p: progress_bar.progress(p))
                
                # Compare torrents
                st.write("Comparing torrents...")
                matches = compare_torrents(torrents)

                if matches:
                    showMatches(matches)
                else:
                    st.warning("No identical torrents found.")

                if st.session_state.show_all_torrents:
                # # Display torrents in tables
                    showTorrents(torrents)

                # Clear progress bar and status text
                progress_bar.empty()
                status_text.empty()
            except Exception as e:
                st.error(f"An error occurred: {e}")

#################### Search #########################
elif page == "Search":
    st.title("Search for Cross Torrents")
    st.session_state.u_input = st.text_input(
        "Search for Title:", value=st.session_state.u_input
    )
    if st.button("Search!"):
        try:
            status_text = st.empty()

            torrents = fetch_torrents_multi(indexer_ids=[tracker_id for i, tracker_id in enumerate(trackers)], title=st.session_state.u_input)
            # Compare torrents
            st.write("Comparing torrents...")
            matches = compare_torrents(torrents)
            st.write("Done.")

            if matches:
                showMatches(matches)
            else:
                st.warning("No identical torrents found.")

            if st.session_state.show_all_torrents:
                showTorrents(torrents)

            # Clear progress bar and status text
            status_text.empty()

        except Exception as e:
            st.error(f"An error occurred: {e}")


#################### Tracker IDs #########################
if page == "Tracker":
    st.title("ID and Names of Trackers")
    trackers = fetch_trackers()
    
    if trackers:
        # Sort trackers by ID
        sorted_trackers = sorted(trackers, key=lambda tracker: tracker['id'])
        
        # Display each tracker ID and name
        for tracker in sorted_trackers:
            st.write(f"**{tracker['id']}** | {tracker['name']}")
        