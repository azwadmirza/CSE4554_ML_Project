def _get_db_genres(genre_names):
    genres = []
    if genre_names:
        with Session() as session:
            for genre_name in genre_names:
                genre = session.query(TVDBGenre).filter(func.lower(TVDBGenre.name) == genre_name.lower()).first()
                if not genre:
                    genre = TVDBGenre(name=genre_name)
                    session.add(genre)
                    session.commit()
                genres.append({'id': genre.id, 'name': genre.name})

    return genres