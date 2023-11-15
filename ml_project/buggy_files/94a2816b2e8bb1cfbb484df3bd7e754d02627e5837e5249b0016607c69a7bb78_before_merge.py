    def resolve_host(self):
        optional = [item for item in self.OPTIONAL_HOSTS if item in self.config and self.config[item] != "none"]
        for item in list(self.HOSTS) + optional:
            host = 'HOST_' + item
            self.config[host] = system.resolve_address(self.config[host])