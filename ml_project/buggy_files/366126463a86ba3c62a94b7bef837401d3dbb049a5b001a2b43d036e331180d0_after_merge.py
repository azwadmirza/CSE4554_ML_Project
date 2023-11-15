    def _signature_items(self):
        items = sorted(it for it in self.items()
                       if it[0] not in ['log_level', 'first_touch'])
        return tuple(str(items)) + tuple(str(sorted(self.backend.items())))