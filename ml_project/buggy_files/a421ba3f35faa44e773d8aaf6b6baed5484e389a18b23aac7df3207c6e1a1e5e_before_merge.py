    def __call__(self, attrs):
        # Ensure uniqueness.
        filter_kwargs = dict([
            (field_name, attrs[field_name]) for field_name in self.fields
        ])
        queryset = self.queryset.filter(**filter_kwargs)
        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            field_names = ', '.join(self.fields)
            raise ValidationError(self.message.format(field_names=field_names))