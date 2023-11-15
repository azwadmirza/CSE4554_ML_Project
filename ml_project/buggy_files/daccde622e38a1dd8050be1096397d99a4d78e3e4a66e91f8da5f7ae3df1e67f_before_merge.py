    def excluded_files(self):
        self._check_svn_repo()
        excluded_list = []
        output = self.run("status --no-ignore")
        for it in output.splitlines():
            if it[0] == 'I':  # Only ignored files
                filepath = it[8:].strip()
                excluded_list.append(os.path.normpath(filepath))
        return excluded_list