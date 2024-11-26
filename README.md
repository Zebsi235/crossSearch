# CrossSearch

CrossSearch is a tool designed to identify cross-seedable torrents by searching for torrents with the same name and size across multiple indexers. It leverages the **Prowlarr API** for torrent indexing and **TMDB** or **OMDB API keys** to retrieve top title names, enabling effective comparison of duplicate torrents.

## Features

- **Cross-seed Detection**: Searches for torrents with the same name and size across indexers.
- **API Integration**:
  - **Prowlarr API** for torrent data.
  - **TMDB/OMDB APIs** for retrieving title names for comparison.
- **Docker Support**: Simplified deployment using Docker.

## Usage

1. **Configure Environment Variables**:
   - Use the `.env.example` file as a template.
   - Rename it to `.env`
   - Set the required environment variables (e.g., API keys, Prowlarr host, and port).

2. **Run with Docker**:
   - Build and run the application using Docker:
     ```bash
     docker build -t crosssearch .
     docker run --env-file .env -p 8501:8501 crosssearch
     ```

3. **Access the Application**:
   - Open your browser and navigate to `http://localhost:8501`.

## Environment Variables

The required environment variables include:
- `PROWLARR_API_URL`: URL for the Prowlarr instance.
- `TMDB_API_KEY`: Your TMDB API key.
- `OMDB_API_KEY`: Your OMDB API key. Not used yet.
- `API_KEY_PROWLARR`: Your Prowlarr API key.

Refer to `.env.example` for all configurable parameters.

## Contributing

Contributions are welcome!

## License

This project is licensed under the [MIT License](LICENSE).

## Disclaimer

CrossSearch is designed for personal use only. Ensure compliance with applicable laws and the terms of service of the APIs and indexers used.
