    def register(self):
        # Use a boolean so we can easily convert it to a number in conscience
        self.service_definition['tags']['tag.up'] = self.last_status
        try:
            self.cs.register(self.service['type'], self.service_definition)
        except requests.RequestException as rqe:
            self.logger.warn("Failed to register service %s: %s",
                             self.service_definition["addr"], rqe)