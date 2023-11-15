    def _add_to_anidb_mylist(self, file_path):
        """
        Add an episode to anidb mylist.

        :param file_path: file to add to mylist
        """
        if helpers.set_up_anidb_connection():
            if not self.anidbEpisode:  # seems like we could parse the name before, now lets build the anidb object
                self.anidbEpisode = self._build_anidb_episode(app.ADBA_CONNECTION, file_path)

            self.log(u'Adding the file to the anidb mylist', logger.DEBUG)
            try:
                self.anidbEpisode.add_to_mylist(status=1)  # status = 1 sets the status of the file to "internal HDD"
            except Exception as e:
                self.log(u'Exception message: {0!r}'.format(e))