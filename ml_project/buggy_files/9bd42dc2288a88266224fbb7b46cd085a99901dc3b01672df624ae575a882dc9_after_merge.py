    def fast_sync(self):

        ''' Movie and userdata not provided by server yet.
        '''
        last_sync = settings('LastIncrementalSync')
        include = []
        filters = ["tvshows", "boxsets", "musicvideos", "music", "movies"]
        sync = get_sync()
        LOG.info("--[ retrieve changes ] %s", last_sync)

        # Get the item type of each synced library and build list of types to request
        for item_id in sync['Whitelist']:
            library = self.server.jellyfin.get_item(item_id)
            library_type = library.get('CollectionType')
            if library_type in filters:
                include.append(library_type)

        # Include boxsets if movies are synced
        if 'movies' in include:
            include.append('boxsets')

        # Filter down to the list of library types we want to exclude
        query_filter = list(set(filters) - set(include))

        try:
            updated = []
            userdata = []
            removed = []

            # Get list of updates from server for synced library types and populate work queues
            result = self.server.jellyfin.get_sync_queue(last_sync, ",".join([ x for x in query_filter ]))
            updated.extend(result['ItemsAdded'])
            updated.extend(result['ItemsUpdated'])
            userdata.extend(result['UserDataChanged'])
            removed.extend(result['ItemsRemoved'])

            total = len(updated) + len(userdata)

            if total > int(settings('syncIndicator') or 99):

                ''' Inverse yes no, in case the dialog is forced closed by Kodi.
                '''
                if dialog("yesno", heading="{jellyfin}", line1=translate(33172).replace('{number}', str(total)), nolabel=translate(107), yeslabel=translate(106)):
                    LOG.warning("Large updates skipped.")

                    return True

            self.updated(updated)
            self.userdata(userdata)
            self.removed(removed)

        except Exception as error:
            LOG.exception(error)

            return False

        return True