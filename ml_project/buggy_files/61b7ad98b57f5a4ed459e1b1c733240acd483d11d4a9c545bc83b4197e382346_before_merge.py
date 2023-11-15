    def process(self, resources, events=None):
        if self.manager:
            sweeper = AnnotationSweeper(self.manager.get_model().id, resources)

        for f in self.filters:
            resources = f.process(resources, events)

        if self.manager:
            sweeper.sweep(resources)

        return resources