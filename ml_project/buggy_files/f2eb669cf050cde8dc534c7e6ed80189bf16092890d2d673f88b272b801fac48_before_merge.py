    def uninstall_repo(self, name):
        repo_path = path.join(self.plugin_dir, name)
        shutil.rmtree(repo_path)
        repos = self.get_installed_plugin_repos().pop(name)
        self.set_plugin_repos(repos)