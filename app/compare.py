from collections import defaultdict
import  re 
import streamlit as st # Debug only
def normalize_title(title):
    """
    Normalize the title by removing special characters, converting to lowercase,
    and removing the .mkv extension if it exists.
    """
    title = title.lower()
    title = re.sub(r'\.mkv', '', title)  # Remove .mkv extension if it exists
    title = re.sub(r'\s+', '', title)  # Normalize whitespaces
    title = re.sub(r'[^\w\s]', '', title)  # Remove punctuation
    return title.strip()


def compare_torrents(all_torrents):

    grouped_torrents = defaultdict(list)

    # Normalize titles and group torrents by normalized title
    for torrent in all_torrents:
        normalized_title = normalize_title(torrent['title'])
        #st.write(f"Adding {torrent} to size group {normalized_title}")
        grouped_torrents[normalized_title].append(torrent)

    matches = []

    # Check for multiple indexers and same size within each title group
    for title, torrents in grouped_torrents.items():
        # Group torrents by size
        size_groups = defaultdict(list)
        for torrent in torrents:
            norm_size = int(torrent['size'])

            size_groups[norm_size].append(torrent)
        #st.write(size_groups)
        # For each size group, check if there are torrents from multiple indexers
        for size, torrents_with_same_size in size_groups.items():
            indexers = {torrent['indexer'] for torrent in torrents_with_same_size}

            if len(indexers) > 1:  # If there are torrents from multiple indexers
                matches.append({
                    "title": title,
                    "size": size,
                    "indexers": list(indexers),
                    "matched_torrents": torrents_with_same_size
                })

    return matches