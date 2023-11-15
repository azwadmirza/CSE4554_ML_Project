    def process_new_repo(self, result):
        if result['returncode'] == 0:
            new_repo = RepoModel.get(url=result['params']['repo_url'])
            profile = self.profile()
            profile.repo = new_repo.id
            profile.save()

            self.set_repos()
            self.repoSelector.setCurrentIndex(self.repoSelector.count() - 1)
            self.repo_added.emit()
            self.init_repo_stats()