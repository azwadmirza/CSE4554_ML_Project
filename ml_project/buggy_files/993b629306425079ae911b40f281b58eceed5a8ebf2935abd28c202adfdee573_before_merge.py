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

        try:
            if not os.path.isdir(nfo_file_dir):
                log.debug('Metadata directory did not exist, creating it at {location}',
                          {'location': nfo_file_dir})
                os.makedirs(nfo_file_dir)
                helpers.chmod_as_parent(nfo_file_dir)

            log.debug('Writing episode nfo file to {location}',
                      {'location': nfo_file_path})

            with io.open(nfo_file_path, 'wb') as nfo_file:
                # Calling encode directly, b/c often descriptions have wonky characters.
                data.write(nfo_file, encoding='utf-8', xml_declaration=True)

            helpers.chmod_as_parent(nfo_file_path)

        except IOError as e:
            log.error('Unable to write file to {location} - are you sure the folder is writable? {error}',
                      {'location': nfo_file_path, 'error': ex(e)})
            return False

        return True