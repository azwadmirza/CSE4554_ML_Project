    def prefetch(self):
        return self.select_related(
            'component', 'component__project', 'language'
        ).prefetch_related(
            'component__alert_set', 'language__plural_set'
        )