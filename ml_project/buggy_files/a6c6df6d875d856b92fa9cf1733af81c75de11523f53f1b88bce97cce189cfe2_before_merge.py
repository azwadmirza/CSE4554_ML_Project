    def compute(self, conn, data=None):
        tarinfo = TarInfo()
        tarinfo.name = self.name
        tarinfo.mod = 0o700
        tarinfo.uid = 0
        tarinfo.gid = 0
        tarinfo.type = REGTYPE
        tarinfo.linkname = ""

        if self.name == CONTAINER_PROPERTIES:
            meta = data or conn.container_get_properties(self.acct, self.ref)
            tarinfo.size = len(json.dumps(meta['properties'], sort_keys=True))
            self._filesize = tarinfo.size
            self._buf = tarinfo.tobuf(format=PAX_FORMAT)
            return
        elif self.name == CONTAINER_MANIFEST:
            tarinfo.size = len(json.dumps(data, sort_keys=True))
            self._filesize = tarinfo.size
            self._buf = tarinfo.tobuf(format=PAX_FORMAT)
            return

        entry = conn.object_get_properties(self.acct, self.ref, self.name)

        properties = entry['properties']

        # x-static-large-object
        if properties.get(SLO, False):
            tarinfo.size = int(properties.get(SLO_SIZE))
            _, slo = conn.object_fetch(self.acct, self.ref, self.name)
            self._slo = json.loads("".join(slo), object_pairs_hook=OrderedDict)
            self._checksums = {}
            # format MD5 to share same format as multi chunks object
            offset = 0
            for idx, ck in enumerate(self._slo):
                self._checksums[idx] = {
                    'hash': ck['hash'].upper(),
                    'size': ck['bytes'],
                    'offset': offset
                }
                offset += ck['bytes']
        else:
            tarinfo.size = int(entry['length'])
            meta, chunks = conn.object_locate(self.acct, self.ref, self.name)
            storage_method = STORAGE_METHODS.load(meta['chunk_method'])
            chunks = _sort_chunks(chunks, storage_method.ec)
            for idx in chunks:
                chunks[idx] = chunks[idx][0]
                del chunks[idx]['url']
                del chunks[idx]['score']
                del chunks[idx]['pos']
            self._checksums = chunks
        self._filesize = tarinfo.size

        # XATTR
        # do we have to store basic properties like policy, ... ?
        for key, val in properties.items():
            assert isinstance(val, basestring), \
                "Invalid type for %s:%s:%s" % (self.acct, self.name, key)
            if self.slo and key in SLO_HEADERS:
                continue
            tarinfo.pax_headers[SCHILY + key] = val
        tarinfo.pax_headers['mime_type'] = entry['mime_type']
        self._buf = tarinfo.tobuf(format=PAX_FORMAT)