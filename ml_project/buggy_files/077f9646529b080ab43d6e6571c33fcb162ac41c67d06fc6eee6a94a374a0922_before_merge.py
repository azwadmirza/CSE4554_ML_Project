def _get_db_genres(genre_names, session=None):
    genres = []
    if genre_names:
        for genre_name in genre_names:
            genre = session.query(TVDBGenre).filter(TVDBGenre.name == genre_name).first()
            if not genre:
                genre = TVDBGenre(name=genre_name)
                session.add(genre)
            genres.append({'id': genre.id, 'name': genre.name})

    return genres