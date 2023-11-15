    def process(self, resources):
        tags = self.data.get('tags', [DEFAULT_TAG])
        batch_size = self.data.get('batch_size', self.batch_size)

        with self.executor_factory(max_workers=self.concurrency) as w:
            futures = []
            for resource_set in utils.chunks(resources, size=batch_size):
                futures.append(
                    w.submit(self.process_resource_set, resource_set, tags))

            for f in as_completed(futures):
                if f.exception():
                    self.log.error(
                        "Exception removing tags: %s on resources:%s \n %s" % (
                            tags, self.id_key, f.exception()))