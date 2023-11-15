    def delete(self):
        """Deletes the rule in AWS"""
        self.remove_all_targets()
        response = self.client.delete_rule(Name=self.name)
        self.changed = True
        return response