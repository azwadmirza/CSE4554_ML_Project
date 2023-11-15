    def disable(self):
        """Disables the rule in AWS"""
        response = self.client.disable_rule(Name=self.name)
        self.changed = True
        return response