    def process(self, resources, event=None):
        days = self.data.get('days', 14)
        duration = timedelta(days)

        self.metric = self.data['name']
        self.end = datetime.utcnow()
        self.start = self.end - duration
        self.period = int(self.data.get('period', duration.total_seconds()))
        self.statistics = self.data.get('statistics', 'Average')
        self.model = self.manager.query.resolve(self.manager.resource_type)
        self.op = OPERATORS[self.data.get('op', 'less-than')]
        self.value = self.data['value']

        ns = self.data.get('namespace')
        if not ns:
            ns = getattr(self.model, 'default_namespace', None)
            if not ns:
                ns = self.DEFAULT_NAMESPACE[self.model.service]
        self.namespace = ns

        self.log.debug("Querying metrics for %d", len(resources))
        matched = []
        with self.executor_factory(max_workers=3) as w:
            futures = []
            for resource_set in chunks(resources, 50):
                futures.append(
                    w.submit(self.process_resource_set, resource_set))

            for f in as_completed(futures):
                if f.exception():
                    self.log.warning(
                        "CW Retrieval error: %s" % f.exception())
                    continue
                matched.extend(f.result())
        return matched