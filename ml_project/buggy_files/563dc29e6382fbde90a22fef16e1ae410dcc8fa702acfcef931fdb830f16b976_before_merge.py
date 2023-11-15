    def set_context(self, serializer):
        # Determine the existing instance, if this is an update operation.
        self.instance = getattr(serializer, 'instance', None)