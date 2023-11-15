    def get_serializer_fields(self, path, method, callback, view):
        """
        Return a list of `coreapi.Field` instances corresponding to any
        request body input, as determined by the serializer class.
        """
        if method not in ('PUT', 'PATCH', 'POST'):
            return []

        fields = []

        serializer_class = view.get_serializer_class()
        serializer = serializer_class()

        if isinstance(serializer, serializers.ListSerializer):
            return coreapi.Field(name='data', location='body', required=True)

        if not isinstance(serializer, serializers.Serializer):
            return []

        for field in serializer.fields.values():
            if field.read_only:
                continue
            required = field.required and method != 'PATCH'
            field = coreapi.Field(name=field.source, location='form', required=required)
            fields.append(field)

        return fields