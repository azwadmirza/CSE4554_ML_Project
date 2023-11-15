    def _ep_data(self, ep_obj):
        """
        Creates an elementTree XML structure for a MediaBrowser style episode.xml
        and returns the resulting data object.

        show_obj: a Series instance to create the NFO for
        """

        eps_to_write = [ep_obj] + ep_obj.related_episodes

        my_show = self._get_show_data(ep_obj.series)
        if not my_show:
            return None

        root_node = etree.Element('details')
        movie = etree.SubElement(root_node, 'movie')

        movie.attrib['isExtra'] = 'false'
        movie.attrib['isSet'] = 'false'
        movie.attrib['isTV'] = 'true'

        # write an MediaBrowser XML containing info for all matching episodes
        for ep_to_write in eps_to_write:

            try:
                my_ep = my_show[ep_to_write.season][ep_to_write.episode]
            except (IndexerEpisodeNotFound, IndexerSeasonNotFound):
                log.info(
                    'Unable to find episode {ep_num} on {indexer}...'
                    ' has it been removed? Should I delete from db?', {
                        'ep_num': episode_num(ep_to_write.season, ep_to_write.episode),
                        'indexer': indexerApi(ep_obj.series.indexer).name,
                    }
                )
                return None

            if ep_to_write == ep_obj:
                # root (or single) episode

                # default to today's date for specials if firstaired is not set
                if ep_to_write.season == 0 and not getattr(my_ep, 'firstaired', None):
                    my_ep['firstaired'] = str(datetime.date.fromordinal(1))

                if not (getattr(my_ep, 'episodename', None) and getattr(my_ep, 'firstaired', None)):
                    return None

                episode = movie

                if ep_to_write.name:
                    episode_name = etree.SubElement(episode, 'title')
                    episode_name.text = ep_to_write.name

                season_number = etree.SubElement(episode, 'season')
                season_number.text = str(ep_to_write.season)

                episode_number = etree.SubElement(episode, 'episode')
                episode_number.text = str(ep_to_write.episode)

                if getattr(my_show, 'firstaired', None):
                    try:
                        year_text = str(datetime.datetime.strptime(my_show['firstaired'], dateFormat).year)
                        if year_text:
                            year = etree.SubElement(episode, 'year')
                            year.text = year_text
                    except Exception:
                        pass

                if getattr(my_show, 'overview', None):
                    plot = etree.SubElement(episode, 'plot')
                    plot.text = my_show['overview']

                if ep_to_write.description:
                    overview = etree.SubElement(episode, 'episodeplot')
                    overview.text = ep_to_write.description

                if getattr(my_show, 'contentrating', None):
                    mpaa = etree.SubElement(episode, 'mpaa')
                    mpaa.text = my_show['contentrating']

                if not ep_obj.related_episodes and getattr(my_ep, 'rating', None):
                    try:
                        rating = int((float(my_ep['rating']) * 10))
                    except ValueError:
                        rating = 0

                    if rating:
                        rating = etree.SubElement(episode, 'rating')
                        rating.text = str(rating)

                if getattr(my_ep, 'director', None):
                    director = etree.SubElement(episode, 'director')
                    director.text = my_ep['director']

                if getattr(my_ep, 'writer', None):
                    writer = etree.SubElement(episode, 'credits')
                    writer.text = my_ep['writer']

                if getattr(my_show, '_actors', None) or getattr(my_ep, 'gueststars', None):
                    cast = etree.SubElement(episode, 'cast')
                    if getattr(my_ep, 'gueststars', None) and isinstance(my_ep['gueststars'], string_types):
                        for actor in (x.strip() for x in my_ep['gueststars'].split('|') if x.strip()):
                            cur_actor = etree.SubElement(cast, 'actor')
                            cur_actor.text = actor

                    if getattr(my_show, '_actors', None):
                        for actor in my_show['_actors']:
                            if 'name' in actor and actor['name'].strip():
                                cur_actor = etree.SubElement(cast, 'actor')
                                cur_actor.text = actor['name'].strip()

            else:
                # append data from (if any) related episodes

                if ep_to_write.name:
                    if not episode_name.text:
                        episode_name.text = ep_to_write.name
                    else:
                        episode_name.text = ', '.join([episode_name.text, ep_to_write.name])

                if ep_to_write.description:
                    if not overview.text:
                        overview.text = ep_to_write.description
                    else:
                        overview.text = '\r'.join([overview.text, ep_to_write.description])

        # Make it purdy
        helpers.indent_xml(root_node)

        data = etree.ElementTree(root_node)

        return data