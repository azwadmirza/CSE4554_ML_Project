    def pickManualSearch(self, provider=None, rowid=None, manual_search_type='episode'):
        """
        Tries to Perform the snatch for a manualSelected episode, episodes or season pack.

        @param provider: The provider id, passed as usenet_crawler and not the provider name (Usenet-Crawler)
        @param rowid: The provider's cache table's rowid. (currently the implicit sqlites rowid is used, needs to be replaced in future)
        @param manual_search_type: Episode or Season search

        @return: A json with a {'success': true} or false.
        """

        # Try to retrieve the cached result from the providers cache table.
        # @TODO: the implicit sqlite rowid is used, should be replaced with an explicit PK column

        try:
            main_db_con = db.DBConnection('cache.db')
            cached_result = main_db_con.action(
                b'SELECT * '
                b'FROM \'{provider}\' '
                b'WHERE rowid = ?'.format(provider=provider),
                [rowid],
                fetchone=True
            )
        except Exception as msg:
            error_message = 'Couldn\'t read cached results. Error: {error}'.format(error=msg)
            logger.log(error_message)
            return self._genericMessage('Error', error_message)

        if not cached_result or not all([cached_result[b'url'],
                                         cached_result[b'quality'],
                                         cached_result[b'name'],
                                         cached_result[b'indexer'],
                                         cached_result[b'indexerid'],
                                         cached_result[b'season'] is not None,
                                         provider]):
            return self._genericMessage('Error', "Cached result doesn't have all needed info to snatch episode")

        try:
            series_obj = Show.find_by_id(app.showList, cached_result[b'indexer'], cached_result[b'indexerid'])
        except (ValueError, TypeError):
            return self._genericMessage('Error', 'Invalid show ID: {0}'.format(cached_result[b'indexerid']))

        if not series_obj:
            return self._genericMessage('Error', 'Could not find a show with id {0} in the list of shows, '
                                                 'did you remove the show?'.format(cached_result[b'indexerid']))

        # Create a list of episode object(s)
        # Multi-episode: |1|2|
        # Single-episode: |1|
        # Season pack: || so we need to get all episodes from season and create all ep objects
        ep_objs = []
        if manual_search_type == 'episode':
            for episode in cached_result[b'episodes'].strip('|').split('|'):
                ep_objs.append(series_obj.get_episode(int(cached_result[b'season']), int(episode)))
        elif manual_search_type == 'season':
            ep_objs.extend(series_obj.get_all_episodes([int(cached_result[b'season'])]))

        # Create the queue item
        snatch_queue_item = ManualSnatchQueueItem(series_obj, ep_objs, provider, cached_result)

        # Add the queue item to the queue
        app.manual_snatch_scheduler.action.add_item(snatch_queue_item)

        while snatch_queue_item.success is not False:
            if snatch_queue_item.started and snatch_queue_item.success:
                # If the snatch was successfull we'll need to update the original searched segment,
                # with the new status: SNATCHED (2)
                update_finished_search_queue_item(snatch_queue_item)
                return json.dumps({
                    'result': 'success',
                })
            time.sleep(1)

        return json.dumps({
            'result': 'failure',
        })