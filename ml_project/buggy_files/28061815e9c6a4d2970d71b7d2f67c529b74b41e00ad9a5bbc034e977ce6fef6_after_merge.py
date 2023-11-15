    def prefetch(self):
        return self.select_related(
            'project', 'linked_component', 'linked_component__project',
        ).prefetch_related('alert_set')