    def extra_attributes(self):
        attributes = {}
        for listener in self.listeners:
            attributes.update(listener)

        return attributes