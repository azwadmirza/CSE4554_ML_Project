    def set_context(self, serializer_field):
        self.user = serializer_field.context['request'].user