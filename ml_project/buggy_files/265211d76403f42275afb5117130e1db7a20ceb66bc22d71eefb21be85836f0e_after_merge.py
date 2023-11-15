    def get_bound_field(self, form, field_name):
        bound_field = BoundField(form, self, field_name)

        # Modify the QuerySet of the field before we return it. Limit choices to any data already bound: Options
        # will be populated on-demand via the APISelect widget.
        data = bound_field.data or bound_field.initial
        if data:
            filter = self.filter(field_name=self.to_field_name or 'pk', queryset=self.queryset)
            self.queryset = filter.filter(self.queryset, data)
        else:
            self.queryset = self.queryset.none()

        return bound_field