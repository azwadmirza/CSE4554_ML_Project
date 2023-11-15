    def _parse_actors(self, tvmaze_id):
        """Parsers actors XML, from
        http://theTMDB.com/api/[APIKEY]/series/[SERIES ID]/actors.xml

        Actors are retrieved using t['show name]['_actors'], for example:

        >>> t = TVMaze(actors = True)
        >>> actors = t['scrubs']['_actors']
        >>> type(actors)
        <class 'TMDB_api.Actors'>
        >>> type(actors[0])
        <class 'TMDB_api.Actor'>
        >>> actors[0]
        <Actor "Zach Braff">
        >>> sorted(actors[0].keys())
        ['id', 'image', 'name', 'role', 'sortorder']
        >>> actors[0]['name']
        u'Zach Braff'
        >>> actors[0]['image']
        u'http://theTMDB.com/banners/actors/43640.jpg'

        Any key starting with an underscore has been processed (not the raw
        data from the indexer)
        """
        logger.debug('Getting actors for %s', [tvmaze_id])
        try:
            actors = self.tvmaze_api.show_cast(tvmaze_id)
        except CastNotFound:
            logger.debug('Actors result returned zero')
            return
        except BaseError as e:
            logger.warning('Getting actors failed. Cause: %s', e)
            return

        cur_actors = Actors()
        for order, cur_actor in enumerate(actors.people):
            save_actor = Actor()
            save_actor['id'] = cur_actor.id
            save_actor['image'] = cur_actor.image.get('original') if cur_actor.image else ''
            save_actor['name'] = cur_actor.name
            save_actor['role'] = cur_actor.character.name
            save_actor['sortorder'] = order
            cur_actors.append(save_actor)
        self._set_show_data(tvmaze_id, '_actors', cur_actors)