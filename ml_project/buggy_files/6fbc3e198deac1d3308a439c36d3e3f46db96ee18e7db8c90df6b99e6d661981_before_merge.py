    def _map_serializer_field(self, field, direction, collect_meta=True):
        if collect_meta:
            meta = self._get_serializer_field_meta(field)
        else:
            meta = {}

        if has_override(field, 'field'):
            override = get_override(field, 'field')
            if is_basic_type(override):
                schema = build_basic_type(override)
                if schema is None:
                    return None
            elif isinstance(override, dict):
                schema = override
            else:
                schema = self._map_serializer_field(force_instance(override), direction, False)

            field_component_name = get_override(field, 'field_component_name')
            if field_component_name:
                component = ResolvedComponent(
                    name=field_component_name,
                    type=ResolvedComponent.SCHEMA,
                    schema=schema,
                    object=field,
                )
                self.registry.register_on_missing(component)
                return append_meta(component.ref, meta)
            else:
                return append_meta(schema, meta)

        serializer_field_extension = OpenApiSerializerFieldExtension.get_match(field)
        if serializer_field_extension:
            schema = serializer_field_extension.map_serializer_field(self, direction)
            return append_meta(schema, meta)

        # nested serializer with many=True gets automatically replaced with ListSerializer
        if is_list_serializer(field):
            if is_serializer(field.child):
                component = self.resolve_serializer(field.child, direction)
                return append_meta(build_array_type(component.ref), meta) if component else None
            else:
                schema = self._map_serializer_field(field.child, direction, collect_meta)
                return append_meta(build_array_type(schema), meta)

        # nested serializer
        if is_serializer(field):
            component = self.resolve_serializer(field, direction)
            return append_meta(component.ref, meta) if component else None

        # Related fields.
        if isinstance(field, serializers.ManyRelatedField):
            schema = self._map_serializer_field(field.child_relation, direction, collect_meta)
            # remove hand-over initkwargs applying only to outer scope
            schema.pop('description', None)
            schema.pop('readOnly', None)
            return append_meta(build_array_type(schema), meta)

        if isinstance(field, serializers.PrimaryKeyRelatedField):
            # read_only fields do not have a Manager by design. go around and get field
            # from parent. also avoid calling Manager. __bool__ as it might be customized
            # to hit the database.
            if getattr(field, 'queryset', None) is not None:
                model_field = field.queryset.model._meta.pk
            else:
                if isinstance(field.parent, serializers.ManyRelatedField):
                    model = field.parent.parent.Meta.model
                    source = field.parent.source.split('.')
                else:
                    model = field.parent.Meta.model
                    source = field.source.split('.')

                # estimates the relating model field and jumps to it's target model PK field.
                # also differentiate as source can be direct (pk) or relation field (model).
                model_field = follow_field_source(model, source)
                if anyisinstance(model_field, [models.ForeignKey, models.ManyToManyField]):
                    model_field = model_field.target_field

            # primary keys are usually non-editable (readOnly=True) and map_model_field correctly
            # signals that attribute. however this does not apply in the context of relations.
            schema = self._map_model_field(model_field, direction)
            schema.pop('readOnly', None)
            return append_meta(schema, meta)

        if isinstance(field, serializers.StringRelatedField):
            return append_meta(build_basic_type(OpenApiTypes.STR), meta)

        if isinstance(field, serializers.SlugRelatedField):
            return append_meta(build_basic_type(OpenApiTypes.STR), meta)

        if isinstance(field, serializers.HyperlinkedIdentityField):
            return append_meta(build_basic_type(OpenApiTypes.URI), meta)

        if isinstance(field, serializers.HyperlinkedRelatedField):
            return append_meta(build_basic_type(OpenApiTypes.URI), meta)

        if isinstance(field, serializers.MultipleChoiceField):
            return append_meta(build_array_type(build_choice_field(field)), meta)

        if isinstance(field, serializers.ChoiceField):
            return append_meta(build_choice_field(field), meta)

        if isinstance(field, serializers.ListField):
            if isinstance(field.child, _UnvalidatedField):
                return append_meta(build_array_type({}), meta)
            elif is_serializer(field.child):
                component = self.resolve_serializer(field.child, direction)
                return append_meta(build_array_type(component.ref), meta) if component else None
            else:
                schema = self._map_serializer_field(field.child, direction, collect_meta)
                return append_meta(build_array_type(schema), meta)

        # DateField and DateTimeField type is string
        if isinstance(field, serializers.DateField):
            return append_meta(build_basic_type(OpenApiTypes.DATE), meta)

        if isinstance(field, serializers.DateTimeField):
            return append_meta(build_basic_type(OpenApiTypes.DATETIME), meta)

        if isinstance(field, serializers.TimeField):
            return append_meta(build_basic_type(OpenApiTypes.TIME), meta)

        if isinstance(field, serializers.EmailField):
            return append_meta(build_basic_type(OpenApiTypes.EMAIL), meta)

        if isinstance(field, serializers.URLField):
            return append_meta(build_basic_type(OpenApiTypes.URI), meta)

        if isinstance(field, serializers.UUIDField):
            return append_meta(build_basic_type(OpenApiTypes.UUID), meta)

        if isinstance(field, serializers.DurationField):
            return append_meta(build_basic_type(OpenApiTypes.STR), meta)

        if isinstance(field, serializers.IPAddressField):
            # TODO this might be a DRF bug. protocol is not propagated to serializer although it
            #  should have been. results in always 'both' (thus no format)
            if 'ipv4' == field.protocol.lower():
                schema = build_basic_type(OpenApiTypes.IP4)
            elif 'ipv6' == field.protocol.lower():
                schema = build_basic_type(OpenApiTypes.IP6)
            else:
                schema = build_basic_type(OpenApiTypes.STR)
            return append_meta(schema, meta)

        # DecimalField has multipleOf based on decimal_places
        if isinstance(field, serializers.DecimalField):
            if getattr(field, 'coerce_to_string', api_settings.COERCE_DECIMAL_TO_STRING):
                content = {**build_basic_type(OpenApiTypes.STR), 'format': 'decimal'}
            else:
                content = build_basic_type(OpenApiTypes.DECIMAL)

            if field.max_whole_digits:
                content['maximum'] = int(field.max_whole_digits * '9') + 1
                content['minimum'] = -content['maximum']
            self._map_min_max(field, content)
            return append_meta(content, meta)

        if isinstance(field, serializers.FloatField):
            content = build_basic_type(OpenApiTypes.FLOAT)
            self._map_min_max(field, content)
            return append_meta(content, meta)

        if isinstance(field, serializers.IntegerField):
            content = build_basic_type(OpenApiTypes.INT)
            self._map_min_max(field, content)
            # 2147483647 is max for int32_size, so we use int64 for format
            if int(content.get('maximum', 0)) > 2147483647 or int(content.get('minimum', 0)) > 2147483647:
                content['format'] = 'int64'
            return append_meta(content, meta)

        if isinstance(field, serializers.FileField):
            if spectacular_settings.COMPONENT_SPLIT_REQUEST and direction == 'request':
                content = build_basic_type(OpenApiTypes.BINARY)
            else:
                use_url = getattr(field, 'use_url', api_settings.UPLOADED_FILES_USE_URL)
                content = build_basic_type(OpenApiTypes.URI if use_url else OpenApiTypes.STR)
            return append_meta(content, meta)

        if isinstance(field, serializers.SerializerMethodField):
            method = getattr(field.parent, field.method_name)
            return append_meta(self._map_response_type_hint(method), meta)

        if anyisinstance(field, [serializers.BooleanField, serializers.NullBooleanField]):
            return append_meta(build_basic_type(OpenApiTypes.BOOL), meta)

        if isinstance(field, serializers.JSONField):
            return append_meta(build_basic_type(OpenApiTypes.OBJECT), meta)

        if anyisinstance(field, [serializers.DictField, serializers.HStoreField]):
            content = build_basic_type(OpenApiTypes.OBJECT)
            if not isinstance(field.child, _UnvalidatedField):
                content['additionalProperties'] = self._map_serializer_field(
                    field.child, direction, collect_meta
                )
            return append_meta(content, meta)

        if isinstance(field, serializers.CharField):
            return append_meta(build_basic_type(OpenApiTypes.STR), meta)

        if isinstance(field, serializers.ReadOnlyField):
            # direct source from the serializer
            assert field.source_attrs, f'ReadOnlyField "{field}" needs a proper source'
            target = follow_field_source(field.parent.Meta.model, field.source_attrs)

            if callable(target):
                schema = self._map_response_type_hint(target)
            elif isinstance(target, models.Field):
                schema = self._map_model_field(target, direction)
            else:
                assert False, f'ReadOnlyField target "{field}" must be property or model field'
            return append_meta(schema, meta)

        # DRF was not able to match the model field to an explicit SerializerField and therefore
        # used its generic fallback serializer field that simply wraps the model field.
        if isinstance(field, serializers.ModelField):
            schema = self._map_model_field(field.model_field, direction)
            return append_meta(schema, meta)

        warn(f'could not resolve serializer field "{field}". defaulting to "string"')
        return append_meta(build_basic_type(OpenApiTypes.STR), meta)