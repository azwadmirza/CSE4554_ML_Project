    def chunk_audit(self, path):
        with open(path) as f:
            try:
                meta = read_chunk_metadata(f)
            except exc.MissingAttribute as e:
                raise exc.FaultyChunk(
                    'Missing extended attribute %s' % e)
            size = int(meta['chunk_size'])
            md5_checksum = meta['chunk_hash'].lower()
            reader = ChunkReader(f, size, md5_checksum)
            with closing(reader):
                for buf in reader:
                    buf_len = len(buf)
                    self.bytes_running_time = ratelimit(
                        self.bytes_running_time,
                        self.max_bytes_per_second,
                        increment=buf_len)
                    self.bytes_processed += buf_len
                    self.total_bytes_processed += buf_len

            try:
                container_id = meta['container_id']
                content_path = meta['content_path']
                _obj_meta, data = self.container_client.content_locate(
                    cid=container_id, path=content_path, properties=False)

                # Check chunk data
                chunk_data = None
                metachunks = set()
                for c in data:
                    if c['url'].endswith(meta['chunk_id']):
                        metachunks.add(c['pos'].split('.', 2)[0])
                        chunk_data = c
                if not chunk_data:
                    raise exc.OrphanChunk('Not found in content')

                if chunk_data['size'] != int(meta['chunk_size']):
                    raise exc.FaultyChunk('Invalid chunk size found')

                if chunk_data['hash'] != meta['chunk_hash']:
                    raise exc.FaultyChunk('Invalid chunk hash found')

                if chunk_data['pos'] != meta['chunk_pos']:
                    raise exc.FaultyChunk('Invalid chunk position found')

            except exc.NotFound:
                raise exc.OrphanChunk('Chunk not found in container')