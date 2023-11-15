    def _show_data(self, show_obj):
        """
        Creates an elementTree XML structure for a MediaBrowser-style series.xml
        returns the resulting data object.

        show_obj: a Series instance to create the NFO for
        """
        my_show = self._get_show_data(show_obj)

        # If by any reason it couldn't get the shows indexer data let's not go throught the rest of this method
        # as that pretty useless.
        if not my_show:
            return False

        root_node = etree.Element('details')
        tv_node = etree.SubElement(root_node, 'movie')
        tv_node.attrib['isExtra'] = 'false'
        tv_node.attrib['isSet'] = 'false'
        tv_node.attrib['isTV'] = 'true'

        title = etree.SubElement(tv_node, 'title')
        title.text = my_show['seriesname']

        if getattr(my_show, 'genre', None):
            genres = etree.SubElement(tv_node, 'genres')
            for genre in my_show['genre'].split('|'):
                if genre and genre.strip():
                    cur_genre = etree.SubElement(genres, 'Genre')
                    cur_genre.text = genre.strip()

        if getattr(my_show, 'firstaired', None):
            first_aired = etree.SubElement(tv_node, 'premiered')
            first_aired.text = my_show['firstaired']
            try:
                year_text = str(datetime.datetime.strptime(my_show['firstaired'], dateFormat).year)
                if year_text:
                    year = etree.SubElement(tv_node, 'year')
                    year.text = year_text
            except Exception:
                pass

        if getattr(my_show, 'overview', None):
            plot = etree.SubElement(tv_node, 'plot')
            plot.text = my_show['overview']

        if getattr(my_show, 'rating', None):
            try:
                rating = int(float(my_show['rating']) * 10)
            except ValueError:
                rating = 0

            if rating:
                rating = etree.SubElement(tv_node, 'rating')
                rating.text = str(rating)

        if getattr(my_show, 'status', None):
            status = etree.SubElement(tv_node, 'status')
            status.text = my_show['status']

        if getattr(my_show, 'contentrating', None):
            mpaa = etree.SubElement(tv_node, 'mpaa')
            mpaa.text = my_show['contentrating']

        if getattr(my_show, 'imdb_id', None):
            imdb_id = etree.SubElement(tv_node, 'id')
            imdb_id.attrib['moviedb'] = 'imdb'
            imdb_id.text = my_show['imdb_id']

        if getattr(my_show, 'id', None):
            indexer_id = etree.SubElement(tv_node, 'indexerid')
            indexer_id.text = str(my_show['id'])

        if getattr(my_show, 'runtime', None):
            runtime = etree.SubElement(tv_node, 'runtime')
            runtime.text = str(my_show['runtime'])

        if getattr(my_show, '_actors', None):
            cast = etree.SubElement(tv_node, 'cast')
            for actor in my_show['_actors']:
                if 'name' in actor and actor['name'].strip():
                    cur_actor = etree.SubElement(cast, 'actor')
                    cur_actor.text = actor['name'].strip()

        helpers.indent_xml(root_node)

        data = etree.ElementTree(root_node)

        return data