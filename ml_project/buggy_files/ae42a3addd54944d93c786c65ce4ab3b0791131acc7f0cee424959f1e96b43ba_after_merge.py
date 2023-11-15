    def tool_shed_repositories(self):
        try:
            repositories = self.cache.repositories
        except AttributeError:
            self.rebuild()
            repositories = self.cache.repositories
        tool_shed_repositories = [repo for repo in repositories if isinstance(repo, self.app.install_model.ToolShedRepository)]
        if tool_shed_repositories and inspect(tool_shed_repositories[0]).detached:
            self.rebuild()
            repositories = self.cache.repositories
        return repositories