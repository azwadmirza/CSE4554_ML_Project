    def process_set(self, resources, event):
        resource_type = self.manager.get_model()
        resource_map = {r[resource_type.id]: r for r in resources}
        sweeper = AnnotationSweeper(resource_type.id, resources)

        for f in self.filters:
            resources = f.process(resources, event)

        before = set(resource_map.keys())
        after = set([r[resource_type.id] for r in resources])
        results = before - after
        sweeper.sweep([])

        return [resource_map[r_id] for r_id in results]