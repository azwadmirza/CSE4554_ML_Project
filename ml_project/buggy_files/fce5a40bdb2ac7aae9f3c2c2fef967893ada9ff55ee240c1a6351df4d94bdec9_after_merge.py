    def write_ep_file(self, ep_obj):
        """
        Generates and writes ep_obj's metadata under the given path with the
        given filename root. Uses the episode's name with the extension in
        _ep_nfo_extension.

        ep_obj: Episode object for which to create the metadata

        file_name_path: The file name to use for this metadata. Note that the extension
                will be automatically added based on _ep_nfo_extension. This should
                include an absolute path.

        Note that this method expects that _ep_data will return an ElementTree
        object. If your _ep_data returns data in another format you'll need to
        override this method.
        """
        data = self._ep_data(ep_obj)

        if not data:
            return False

        nfo_file_path = self.get_episode_file_path(ep_obj)
        nfo_file_dir = os.path.dirname(nfo_file_path)

        if not (nfo_file_path and nfo_file_dir):
            log.debug(u'Unable to write episode nfo file because episode location is missing.')
            return False

        try:
            if not os.path.isdir(nfo_file_dir):
                log.debug(u'Metadata directory missing, creating it at {location}',
                          {u'location': nfo_file_dir})
                os.makedirs(nfo_file_dir)
                helpers.chmod_as_parent(nfo_file_dir)

            log.debug(u'Writing episode nfo file to {location}',
                      {u'location': nfo_file_path})
            nfo_file = io.open(nfo_file_path, u'wb')
            data.write(nfo_file, encoding=u'UTF-8')
            nfo_file.close()
            helpers.chmod_as_parent(nfo_file_path)
        except IOError as e:
            exception_handler.handle(e, u'Unable to write file to {location}', location=nfo_file_path)
            return False

        return True