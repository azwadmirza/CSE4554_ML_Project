    def remove_targets(self, target_ids):
        """Removes the provided targets from the rule in AWS"""
        if not target_ids:
            return
        request = {
            'Rule': self.name,
            'Ids': target_ids
        }
        response = self.client.remove_targets(**request)
        self.changed = True
        return response