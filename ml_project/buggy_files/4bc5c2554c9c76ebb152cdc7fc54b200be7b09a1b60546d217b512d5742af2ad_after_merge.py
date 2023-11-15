    def object_fetch(self, account, container, obj, version=None, ranges=None,
                     key_file=None, **kwargs):
        """
        Download an object.

        :param account: name of the account in which the object is stored
        :param container: name of the container in which the object is stored
        :param obj: name of the object to fetch
        :param version: version of the object to fetch
        :type version: `str`
        :param ranges: a list of object ranges to download
        :type ranges: `list` of `tuple`
        :param key_file: path to the file containing credentials

        :keyword properties: should the request return object properties
            along with content description (True by default)
        :type properties: `bool`

        :returns: a dictionary of object metadata and
            a stream of object data
        :rtype: tuple
        """
        meta, raw_chunks = self.object_locate(
            account, container, obj, version=version, **kwargs)
        chunk_method = meta['chunk_method']
        storage_method = STORAGE_METHODS.load(chunk_method)
        chunks = _sort_chunks(raw_chunks, storage_method.ec)
        meta['container_id'] = name2cid(account, container).upper()
        meta['ns'] = self.namespace
        self._patch_timeouts(kwargs)
        if storage_method.ec:
            stream = fetch_stream_ec(chunks, ranges, storage_method, **kwargs)
        elif storage_method.backblaze:
            stream = self._fetch_stream_backblaze(meta, chunks, ranges,
                                                  storage_method, key_file,
                                                  **kwargs)
        else:
            stream = fetch_stream(chunks, ranges, storage_method, **kwargs)
        return meta, stream