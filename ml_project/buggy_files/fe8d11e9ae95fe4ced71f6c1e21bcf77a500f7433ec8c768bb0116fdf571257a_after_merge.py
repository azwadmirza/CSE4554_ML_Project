    def process(self, env, cb):
        event = Event(env)
        if event.event_type == EventTypes.CONTENT_DELETED:
            url = event.env.get('url')
            chunks = []
            content_headers = None
            for item in event.data:
                if item.get('type') == 'chunks':
                    chunks.append(item)
                if item.get("type") == 'contents_headers':
                    content_headers = item
            if len(chunks):
                if not content_headers:
                    chunk_method = guess_storage_method(chunks[0]['id']) + '/'
                else:
                    chunk_method = content_headers['chunk-method']
                handler, storage_method = self._load_handler(chunk_method)
                handler(url, chunks, content_headers, storage_method)
                return self.app(env, cb)

        return self.app(env, cb)