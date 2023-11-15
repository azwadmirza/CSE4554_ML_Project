    def __init__(self, metainfo=None, torrent_parameters=None):
        """
        Create a new TorrentDef object, possibly based on existing data.
        :param metainfo: A dictionary with metainfo, i.e. from a .torrent file.
        :param torrent_parameters: User-defined parameters for the new TorrentDef.
        """
        self._logger = logging.getLogger(self.__class__.__name__)
        self.torrent_parameters = {}
        self.metainfo = metainfo
        self.files_list = []
        self.infohash = None
        if metainfo is not None:
            # First, make sure the passed metainfo is valid
            try:
                lt.torrent_info(metainfo)
            except RuntimeError as exc:
                raise ValueError(str(exc))

            self.infohash = sha1(bencode(metainfo[b'info'])).digest()
            self.copy_metainfo_to_torrent_parameters()

        elif torrent_parameters:
            self.torrent_parameters.update(torrent_parameters)