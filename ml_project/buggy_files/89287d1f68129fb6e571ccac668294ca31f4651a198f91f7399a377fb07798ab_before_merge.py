    def check_obj(self, target, recurse=False):
        account = target.account
        container = target.container
        obj = target.obj

        if (account, container, obj) in self.running:
            self.running[(account, container, obj)].wait()
        if (account, container, obj) in self.list_cache:
            return self.list_cache[(account, container, obj)]
        self.running[(account, container, obj)] = Event()
        print('Checking object "%s"' % target)
        container_listing, ct_meta = self.check_container(target)
        error = False
        if obj not in container_listing:
            print('  Object %s missing from container listing' % target)
            error = True
            # checksum = None
        else:
            # TODO check checksum match
            # checksum = container_listing[obj]['hash']
            pass

        results = []
        meta = dict()
        try:
            meta, results = self.container_client.content_locate(
                account=account, reference=container, path=obj)
        except exc.NotFound as e:
            self.object_not_found += 1
            error = True
            print('  Not found object "%s": %s' % (target, str(e)))
        except Exception as e:
            self.object_exceptions += 1
            error = True
            print(' Exception object "%s": %s' % (target, str(e)))

        chunk_listing = dict()
        for chunk in results:
            chunk_listing[chunk['url']] = chunk

        self.check_obj_policy(target.copy(), meta, results)

        self.objects_checked += 1
        self.list_cache[(account, container, obj)] = (chunk_listing, meta)
        self.running[(account, container, obj)].send(True)
        del self.running[(account, container, obj)]

        if recurse:
            for chunk in chunk_listing:
                t = target.copy()
                t.chunk = chunk
                self.pool.spawn_n(self.check_chunk, t)
        if error and self.error_file:
            self.write_error(target)
        return chunk_listing, meta