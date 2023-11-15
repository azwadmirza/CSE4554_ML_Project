    def __init__(self, uri, min_part_size=WEBHDFS_MIN_PART_SIZE):
        """
        Parameters
        ----------
        min_part_size: int, optional
            For writing only.

        """
        self._uri = uri
        self._closed = False
        self.min_part_size = min_part_size
        # creating empty file first
        payload = {"op": "CREATE", "overwrite": True}
        init_response = requests.put(self._uri, params=payload, allow_redirects=False)
        if not init_response.status_code == httplib.TEMPORARY_REDIRECT:
            raise WebHdfsException.from_response(init_response)
        uri = init_response.headers['location']
        response = requests.put(uri, data="", headers={'content-type': 'application/octet-stream'})
        if not response.status_code == httplib.CREATED:
            raise WebHdfsException.from_response(response)
        self.lines = []
        self.parts = 0
        self.chunk_bytes = 0
        self.total_size = 0

        #
        # This member is part of the io.BufferedIOBase interface.
        #
        self.raw = None