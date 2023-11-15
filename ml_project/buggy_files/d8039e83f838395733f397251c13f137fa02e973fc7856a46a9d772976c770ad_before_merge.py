    def set_context(self, serializer_field):
        self.is_update = serializer_field.parent.instance is not None