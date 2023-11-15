def fetch_albums_from_artist(artist_url, album_type="album"):
    """
    This funcction returns all the albums from a give artist_url using the US
    market
    :param artist_url - spotify artist url
    :param album_type - the type of album to fetch (ex: single) the default is
                        a standard album
    :param return - the album from the artist
    """

    # fetching artist's albums limitting the results to the US to avoid duplicate
    # albums from multiple markets
    artist_id = internals.extract_spotify_id(artist_url)
    results = spotify.artist_albums(artist_id, album_type=album_type, country="US")

    albums = results["items"]

    # indexing all pages of results
    while results["next"]:
        results = spotify.next(results)
        albums.extend(results["items"])

    return albums