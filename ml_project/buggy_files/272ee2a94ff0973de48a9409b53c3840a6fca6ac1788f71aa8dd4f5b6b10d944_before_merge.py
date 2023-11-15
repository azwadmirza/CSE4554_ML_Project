    def checkout(self):
        output = ""
        if self._data.type == "git":
            try:
                output += self.repo.clone(url=self._data.url, branch=self._data.revision, shallow=True)
            except subprocess.CalledProcessError:
                # remove the .git directory, otherwise, fallback clone cannot be successful
                # it's completely safe to do here, as clone without branch expects empty directory
                rmdir(os.path.join(self.repo_folder, ".git"))
                output += self.repo.clone(url=self._data.url, shallow=False)
            output += self.repo.checkout(element=self._data.revision,
                                         submodule=self._data.submodule)
        else:
            output += self.repo.checkout(url=self._data.url, revision=self._data.revision)
        return output