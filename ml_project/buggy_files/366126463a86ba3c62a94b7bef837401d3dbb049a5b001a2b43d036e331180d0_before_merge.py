    def _signature_items(self):
        return tuple(str(sorted(self.items()))) + tuple(str(sorted(self.backend.items())))