    def __call__(self, attrs):
        filter_kwargs = self.get_filter_kwargs(attrs)

        queryset = self.queryset.filter(**filter_kwargs)
        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            message = self.message.format(date_field=self.date_field)
            raise ValidationError({self.field: message})