    def data_status_root(self):
        statuses = set()

        # Paths with status
        lines = self._run(['status']).split('\n')
        lines = list(filter(None, lines))
        if not lines:
            return 'sync'
        for line in lines:
            code = line[0]
            if code == ' ':
                continue
            statuses.add(self._status_translate(code))

        for status in self.DIRSTATUSES:
            if status in statuses:
                return status
        return 'sync'