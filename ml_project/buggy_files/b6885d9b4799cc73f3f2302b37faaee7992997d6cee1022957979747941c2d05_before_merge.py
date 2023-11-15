    def enable(self):
        """Enables the rule in AWS"""
        response = self.client.enable_rule(Name=self.name)
        self.changed = True
        return response