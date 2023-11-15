    def get(self, title, session=None):
        args = lookup_parser.parse_args()
        include_actors = args.pop('include_actors')
        include_translations = args.pop('include_translations')
        kwargs = args
        kwargs['title'] = title
        try:
            series = at.lookup_series(session=session, **kwargs)
        except LookupError as e:
            return {'status': 'error',
                    'message': e.args[0]
                    }, 404
        result = series.to_dict()
        if include_actors:
            result["actors"] = list_actors(series.actors)
        if include_translations:
            result["translations"] = get_translations(series.translate)
        return jsonify(result)