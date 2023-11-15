def write_all_albums_from_artist(artist_url, text_file=None):
    """
    This function gets all albums from an artist and writes it to a file in the
    current working directory called [ARTIST].txt, where [ARTIST] is the artist
    of the album
    :param artist_url - spotify artist url
    :param text_file - file to write albums to
    """

    album_base_url = "https://open.spotify.com/album/"

    # fetching all default albums
    albums = fetch_albums_from_artist(artist_url)

    # if no file if given, the default save file is in the current working
    # directory with the name of the artist
    if text_file is None:
        text_file = albums[0]["artists"][0]["name"] + ".txt"

    for album in albums:
        # logging album name
        log.info("Fetching album: " + album["name"])
        write_album(album_base_url + album["id"], text_file=text_file)

    # fetching all single albums
    singles = fetch_albums_from_artist(artist_url, album_type="single")

    for single in singles:
        log.info("Fetching single: " + single["name"])
        write_album(album_base_url + single["id"], text_file=text_file)