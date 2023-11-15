    def set_context(self, serializer):
        """
        This hook is called by the serializer instance,
        prior to the validation call being made.
        """
        # Determine the underlying model field names. These may not be the
        # same as the serializer field names if `source=<>` is set.
        self.field_name = serializer.fields[self.field].source_attrs[0]
        self.date_field_name = serializer.fields[self.date_field].source_attrs[0]
        # Determine the existing instance, if this is an update operation.
        self.instance = getattr(serializer, 'instance', None)