    def save(self, torrent_filepath=None):
        """
        Generate the metainfo and save the torrent file.
        :param torrent_filepath: An optional absolute path to where to save the generated .torrent file.
        """
        torrent_dict = create_torrent_file(self.files_list, self.torrent_parameters, torrent_filepath=torrent_filepath)
        self.metainfo = bdecode_compat(torrent_dict['metainfo'])
        self.copy_metainfo_to_torrent_parameters()
        self.infohash = torrent_dict['infohash']