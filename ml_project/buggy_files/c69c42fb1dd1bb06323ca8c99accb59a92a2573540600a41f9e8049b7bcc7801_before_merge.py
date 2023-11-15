    def status(self):
        status = super().status()

        if status[str(self)] == "deleted":
            return status

        status = defaultdict(dict)
        info = self.read_params()
        for param in self.params:
            if param not in info.keys():
                st = "deleted"
            elif param not in self.info:
                st = "new"
            elif info[param] != self.info[param]:
                st = "modified"
            else:
                assert info[param] == self.info[param]
                continue

            status[str(self)][param] = st

        return status