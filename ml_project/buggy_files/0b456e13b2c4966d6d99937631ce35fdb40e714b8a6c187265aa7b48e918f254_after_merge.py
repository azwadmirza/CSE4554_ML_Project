    def get_schema_operation_parameters(self, auto_schema, *args, **kwargs):
        if issubclass(self.target_class, SpectacularDjangoFilterBackendMixin):
            warn(
                'DEPRECATED - Spectacular\'s DjangoFilterBackend is superseded by extension. you '
                'can simply restore this to the original class, extensions will take care of the '
                'rest.'
            )

        model = get_view_model(auto_schema.view)
        if not model:
            return []

        filterset_class = self.target.get_filterset_class(auto_schema.view, model.objects.none())
        if not filterset_class:
            return []

        parameters = []
        for field_name, field in filterset_class.base_filters.items():
            parameters.append(build_parameter_type(
                name=field_name,
                required=field.extra['required'],
                location=OpenApiParameter.QUERY,
                description=field.label if field.label is not None else field_name,
                schema=self.resolve_filter_field(auto_schema, model, filterset_class, field),
                enum=[c for c, _ in field.extra.get('choices', [])],
            ))

        return parameters