    def prefetch(self):
        return self.select_related(
            'project'
        )