    def uninstall_repo(self, name):
        repo_path = path.join(self.plugin_dir, name)
        shutil.rmtree(repo_path, ignore_errors=True)  # ignore errors because the DB can be desync'ed from the file tree.
        repos = self.get_installed_plugin_repos()
        del(repos[name])
        self.set_plugin_repos(repos)