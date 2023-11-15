    def get(self, title, session=None):
        args = lookup_parser.parse_args()
        include_actors = args.pop('include_actors')
        include_translations = args.pop('include_translations')
        kwargs = args
        kwargs['title'] = title
        try:
            movie = at.lookup_movie(session=session, **kwargs)
        except LookupError as e:
            return {'status': 'error',
                    'message': e.args[0]
                    }, 404
        result = movie.to_dict()
        if include_actors:
            result["actors"] = list_actors(movie.actors)
        if include_translations:
            result["translations"] = get_translations(movie.translate)
        return jsonify(result)