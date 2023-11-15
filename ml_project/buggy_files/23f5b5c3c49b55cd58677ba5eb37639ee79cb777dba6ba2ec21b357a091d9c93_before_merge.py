    def repo_all_list(self, project_key):
        """
        Get all repositories list from project
        :param project_key:
        :return:
        """
        url = self._url_repos(project_key)
        return self.repo_list(url, limit=None)