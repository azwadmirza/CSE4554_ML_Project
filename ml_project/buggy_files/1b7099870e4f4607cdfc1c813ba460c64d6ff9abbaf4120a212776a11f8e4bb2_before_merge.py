def list_actors(actors):
    res = {}
    for actor in actors:
        info = {
            'trakt_id': actor.id,
            'name': actor.name,
            'imdb_id': str(actor.imdb),
            'trakt_slug': actor.slug,
            'tmdb_id': str(actor.tmdb),
            'birthday': actor.birthday.strftime("%Y/%m/%d") if actor.birthday else None,
            'biography': actor.biography,
            'homepage': actor.homepage,
            'death': actor.death.strftime("%Y/%m/%d") if actor.death else None,
            'images': list_images(actor.images)
        }
        res[str(actor.id)] = info
    return res