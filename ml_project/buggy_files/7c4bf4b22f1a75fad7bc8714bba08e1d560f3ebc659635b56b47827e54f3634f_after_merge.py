    def data_status_subpaths(self):
        statuses = {}

        # Paths with status
        lines = self._run(['status']).split('\n')
        lines = list(filter(None, lines))
        for line in lines:
            code, path = line[0], line[8:]
            if code == ' ':
                continue
            statuses[os.path.normpath(path)] = self._status_translate(code)

        return statuses