from collections import defaultdict

def compare_torrents(all_torrents):
    grouped_torrents = defaultdict(list)

    # Group torrents by title (case-insensitive)
    for torrent in all_torrents:
        grouped_torrents[torrent['title']].append(torrent)

    prematches = []
    matches = []

    # Find matches within each group of torrents with the same title
    for title, torrents in grouped_torrents.items():
        if len(torrents) >= 2:  # Only consider titles that appear in more than one tracker
            size_set = set(t['size'] for t in torrents)  # Get unique sizes
            if len(size_set) == 1:  # All torrents must have the same size to match
                prematches.append({
                    "title": title,
                    "size": list(size_set)[0],  # Use the single unique size
                    "indexers": list({t['indexer'] for t in torrents})  # Unique list of indexers
                })

    for match in prematches:
        if len(match["indexers"]) > 1:
            matches.append(match)

    return matches