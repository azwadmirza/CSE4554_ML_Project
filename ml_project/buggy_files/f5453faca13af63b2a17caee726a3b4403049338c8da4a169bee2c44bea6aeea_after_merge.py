    def process_deferred(self):
        """
            Processes options that were deferred in previous calls to set, and
            have since been added.
        """
        update = {}
        for optname, optval in self.deferred.items():
            if optname in self._options:
                optval = self.parse_setval(self._options[optname], optval)
                update[optname] = optval
        self.update(**update)
        for k in update.keys():
            del self.deferred[k]