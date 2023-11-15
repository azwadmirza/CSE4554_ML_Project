    def fast_sync(self):

        ''' Movie and userdata not provided by server yet.
        '''
        last_sync = settings('LastIncrementalSync')
        filters = ["tvshows", "boxsets", "musicvideos", "music", "movies"]
        sync = get_sync()
        LOG.info("--[ retrieve changes ] %s", last_sync)

        try:
            updated = []
            userdata = []
            removed = []

            for media in filters:
                result = self.server.jellyfin.get_sync_queue(last_sync, ",".join([x for x in filters if x != media]))
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

            """
            result = self.server.jellyfin.get_sync_queue(last_sync)
            self.userdata(result['UserDataChanged'])
            self.removed(result['ItemsRemoved'])


            filters.extend(["tvshows", "boxsets", "musicvideos", "music"])

            # Get only movies.
            result = self.server.jellyfin.get_sync_queue(last_sync, ",".join(filters))
            self.updated(result['ItemsAdded'])
            self.updated(result['ItemsUpdated'])
            self.userdata(result['UserDataChanged'])
            self.removed(result['ItemsRemoved'])
            """

        except Exception as error:
            LOG.exception(error)

            return False

        return True