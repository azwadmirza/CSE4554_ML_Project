    def prefetch(self):
        return self.select_related(
            'component', 'component__project', 'language'
        )