    def write_ep_file(self, ep_obj):
        """
        Generates and writes ep_obj's metadata under the given path with the
        given filename root. Uses the episode's name with the extension in
        _ep_nfo_extension.

        ep_obj: Episode object for which to create the metadata

        file_name_path: The file name to use for this metadata. Note that the extension
                will be automatically added based on _ep_nfo_extension. This should
                include an absolute path.
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
                          {'location': nfo_file_dir})
                os.makedirs(nfo_file_dir)
                helpers.chmod_as_parent(nfo_file_dir)

            log.debug(u'Writing episode nfo file to {location}',
                      {'location': nfo_file_path})

            with io.open(nfo_file_path, 'wb') as nfo_file:
                # Calling encode directly, b/c often descriptions have wonky characters.
                nfo_file.write(data.encode('utf-8'))

            helpers.chmod_as_parent(nfo_file_path)

        except EnvironmentError as e:
            log.error(
                u'Unable to write file to {path} - are you sure the folder is writable? {error}',
                {'path': nfo_file_path, 'error': ex(e)}
            )
            return False

        return True