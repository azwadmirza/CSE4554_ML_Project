    def object_fetch(self, account, container, obj, version=None, ranges=None,
                     key_file=None, **kwargs):
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