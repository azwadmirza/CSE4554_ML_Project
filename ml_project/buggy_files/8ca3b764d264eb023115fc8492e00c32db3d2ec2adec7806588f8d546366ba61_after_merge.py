    def _ep_data(self, ep_obj):
        """
        Creates an elementTree XML structure for a WDTV style episode.xml
        and returns the resulting data object.

        ep_obj: a Series instance to create the NFO for
        """

        eps_to_write = [ep_obj] + ep_obj.related_episodes

        my_show = self._get_show_data(ep_obj.series)
        if not my_show:
            return None

        root_node = etree.Element('details')

        # write an WDTV XML containing info for all matching episodes
        for ep_to_write in eps_to_write:

            try:
                my_ep = my_show[ep_to_write.season][ep_to_write.episode]
            except (IndexerEpisodeNotFound, IndexerSeasonNotFound):
                log.info(
                    'Unable to find episode {number} on {indexer}... has it been removed? Should I delete from db?', {
                        'number': ep_num(ep_to_write.season, ep_to_write.episode),
                        'indexer': indexerApi(ep_obj.series.indexer).name,
                    }
                )
                return None

            if ep_obj.season == 0 and not getattr(my_ep, 'firstaired', None):
                my_ep['firstaired'] = str(datetime.date.fromordinal(1))

            if not (getattr(my_ep, 'episodename', None) and getattr(my_ep, 'firstaired', None)):
                return None

            if len(eps_to_write) > 1:
                episode = etree.SubElement(root_node, 'details')
            else:
                episode = root_node

            # TODO: get right EpisodeID
            episode_id = etree.SubElement(episode, 'id')
            episode_id.text = str(ep_to_write.indexerid)

            title = etree.SubElement(episode, 'title')
            title.text = ep_obj.pretty_name()

            if getattr(my_show, 'seriesname', None):
                series_name = etree.SubElement(episode, 'series_name')
                series_name.text = my_show['seriesname']

            if ep_to_write.name:
                episode_name = etree.SubElement(episode, 'episode_name')
                episode_name.text = ep_to_write.name

            season_number = etree.SubElement(episode, 'season_number')
            season_number.text = str(ep_to_write.season)

            episode_num = etree.SubElement(episode, 'episode_number')
            episode_num.text = str(ep_to_write.episode)

            first_aired = etree.SubElement(episode, 'firstaired')

            if ep_to_write.airdate != datetime.date.fromordinal(1):
                first_aired.text = str(ep_to_write.airdate)

            if getattr(my_show, 'firstaired', None):
                try:
                    year_text = str(datetime.datetime.strptime(my_show['firstaired'], dateFormat).year)
                    if year_text:
                        year = etree.SubElement(episode, 'year')
                        year.text = year_text
                except Exception:
                    pass

            if ep_to_write.season != 0 and getattr(my_show, 'runtime', None):
                runtime = etree.SubElement(episode, 'runtime')
                runtime.text = str(my_show['runtime'])

            if getattr(my_show, 'genre', None):
                genre = etree.SubElement(episode, 'genre')
                genre.text = ' / '.join([x.strip() for x in my_show['genre'].split('|') if x.strip()])

            if getattr(my_ep, 'director', None):
                director = etree.SubElement(episode, 'director')
                director.text = my_ep['director']

            if getattr(my_show, '_actors', None):
                for actor in my_show['_actors']:
                    if not ('name' in actor and actor['name'].strip()):
                        continue

                    cur_actor = etree.SubElement(episode, 'actor')

                    cur_actor_name = etree.SubElement(cur_actor, 'name')
                    cur_actor_name.text = actor['name']

                    if 'role' in actor and actor['role'].strip():
                        cur_actor_role = etree.SubElement(cur_actor, 'role')
                        cur_actor_role.text = actor['role'].strip()

            if ep_to_write.description:
                overview = etree.SubElement(episode, 'overview')
                overview.text = ep_to_write.description

            # Make it purdy
            helpers.indent_xml(root_node)
            data = etree.ElementTree(root_node)

        return data