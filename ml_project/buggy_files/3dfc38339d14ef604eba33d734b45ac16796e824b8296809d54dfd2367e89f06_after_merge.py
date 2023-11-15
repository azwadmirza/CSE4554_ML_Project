    def process(self, resources):
        self.id_key = self.manager.get_model().id

        self.preserve = set(self.data.get('preserve'))
        self.space = self.data.get('space', 3)

        with self.executor_factory(max_workers=3) as w:
            list(w.map(self.process_resource, resources))