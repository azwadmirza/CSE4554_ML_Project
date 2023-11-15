    def put_targets(self, targets):
        """Creates or updates the provided targets on the rule in AWS"""
        if not targets:
            return
        request = {
            'Rule': self.name,
            'Targets': self._targets_request(targets),
        }
        response = self.client.put_targets(**request)
        self.changed = True
        return response