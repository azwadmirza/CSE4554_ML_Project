    def tool_shed_repositories(self):
        try:
            repositories = self.cache.repositories
        except AttributeError:
            self.rebuild()
            repositories = self.cache.repositories
        if repositories and not repositories[0]._sa_instance_state._attached:
            self.rebuild()
            repositories = self.cache.repositories
        return repositories