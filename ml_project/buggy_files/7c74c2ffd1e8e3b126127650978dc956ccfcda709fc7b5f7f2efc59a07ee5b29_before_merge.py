    def register(self):
        # Use a boolean so we can easily convert it to a number in conscience
        self.service_definition['tags']['tag.up'] = self.last_status
        self.cs.register(
            self.service['type'], self.service_definition)