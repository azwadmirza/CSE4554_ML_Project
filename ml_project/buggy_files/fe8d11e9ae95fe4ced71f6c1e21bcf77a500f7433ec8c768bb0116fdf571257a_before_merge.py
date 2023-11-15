    def process(self, env, cb):
        event = Event(env)
        if event.event_type == EventTypes.CONTENT_DELETED:
            pile = GreenPile(PARALLEL_CHUNKS_DELETE)
            url = event.env.get('url')
            chunks = []
            content_headers = None
            for item in event.data:
                if item.get('type') == 'chunks':
                    chunks.append(item)
                if item.get("type") == 'contents_headers':
                    content_headers = item
            if len(chunks):
                def delete_chunk(chunk):
                    resp = None
                    p = urlparse(chunk['id'])
                    try:
                        with Timeout(CHUNK_TIMEOUT):
                            conn = http_connect(p.netloc, 'DELETE', p.path)
                            resp = conn.getresponse()
                            resp.chunk = chunk
                    except (Exception, Timeout) as e:
                        self.logger.warn(
                            'error while deleting chunk %s "%s"',
                            chunk['id'], str(e.message))
                    return resp

                def delete_chunk_backblaze(chunks, url, storage_method):
                    meta = {}
                    meta['container_id'] = url['id']
                    chunk_list = []
                    for chunk in chunks:
                        chunk['url'] = chunk['id']
                        chunk_list.append(chunk)
                    key_file = self.conf.get('key_file')
                    backblaze_info = BackblazeUtils.get_credentials(
                        storage_method, key_file)
                    try:
                        BackblazeDeleteHandler(meta, chunk_list,
                                               backblaze_info).delete()
                    except OioException as e:
                        self.logger.warn('delete failed: %s' % str(e))

                chunk_method = content_headers['chunk-method']
                # don't load storage method other than backblaze
                if chunk_method.startswith('backblaze'):
                    storage_method = STORAGE_METHODS.load(chunk_method)
                    delete_chunk_backblaze(chunks, url, storage_method)
                    return self.app(env, cb)
                for chunk in chunks:
                    pile.spawn(delete_chunk, chunk)

                resps = [resp for resp in pile if resp]

                for resp in resps:
                    if resp.status != 204:
                        self.logger.warn(
                            'failed to delete chunk %s (HTTP %s)',
                            resp.chunk['id'], resp.status)
        return self.app(env, cb)