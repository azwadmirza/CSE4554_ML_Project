    def fetch_popular_shows(self, list_type=REQUEST_HOT):
        """Get popular show information from IMDB."""
        series = []
        result = []

        try:
            series = Anidb(cache_dir=join(app.CACHE_DIR, 'simpleanidb')).get_list(list_type)
        except GeneralError as error:
            log.warning('Could not connect to AniDB service: {0}', error)

        for show in series:
            try:
                recommended_show = self._create_recommended_show(show, storage_key='anidb_{0}'.format(show.aid))
                if recommended_show:
                    result.append(recommended_show)
            except MissingTvdbMapping:
                log.info('Could not parse AniDB show {0}, missing tvdb mapping', show.title)
            except Exception:
                log.warning('Could not parse AniDB show, with exception: {0}', traceback.format_exc())

        return result