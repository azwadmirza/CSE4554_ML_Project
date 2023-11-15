    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        super(LocateObject, self).take_action(parsed_args)

        account = self.app.client_manager.get_account()
        container = parsed_args.container
        obj = parsed_args.object
        if parsed_args.auto:
            container = self.flatns_manager(obj)

        data = self.app.client_manager.storage.object_locate(
            account,
            container,
            obj,
            version=parsed_args.object_version,
            properties=False)

        def sort_chunk_pos(c1, c2):
            c1_tokens = c1[0].split('.')
            c2_tokens = c2[0].split('.')
            c1_pos = int(c1_tokens[0])
            c2_pos = int(c2_tokens[0])
            if len(c1_tokens) == 1 or c1_pos != c2_pos:
                return c1_pos - c2_pos
            return cmp(c1[0], c2[0])

        def get_chunks_info(chunks):
            pool_manager = get_pool_manager()
            chunk_hash = ""
            chunk_size = ""
            for c in chunks:
                resp = pool_manager.request('HEAD', c['url'])
                if resp.status != 200:
                    chunk_size = "%d %s" % (resp.status, resp.reason)
                    chunk_hash = "%d %s" % (resp.status, resp.reason)
                else:
                    chunk_size = resp.headers.get(
                        'X-oio-chunk-meta-chunk-size',
                        'Missing chunk size header')
                    chunk_hash = resp.headers.get(
                        'X-oio-chunk-meta-chunk-hash',
                        'Missing chunk hash header')
                yield (c['pos'], c['url'], c['size'], c['hash'], chunk_size,
                       chunk_hash)
        columns = ()
        chunks = []
        if parsed_args.chunk_info:
            columns = ('Pos', 'Id', 'Metachunk size', 'Metachunk hash',
                       'Chunk size', 'Chunk hash')
            chunks = get_chunks_info(data[1])
        else:
            columns = ('Pos', 'Id', 'Metachunk size', 'Metachunk hash')
            chunks = ((c['pos'], c['url'], c['size'],
                       c['hash']) for c in data[1])

        return columns, sorted(chunks, cmp=sort_chunk_pos)