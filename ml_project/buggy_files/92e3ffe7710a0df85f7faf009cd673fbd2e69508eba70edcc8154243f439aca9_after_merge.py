    def _map_model_field(self, model_field, direction):
        assert isinstance(model_field, models.Field)
        # to get a fully initialized serializer field we use DRF's own init logic
        try:
            field_cls, field_kwargs = serializers.ModelSerializer().build_field(
                field_name=model_field.name,
                info=get_field_info(model_field.model),
                model_class=model_field.model,
                nested_depth=0,
            )
            field = field_cls(**field_kwargs)
        except:  # noqa
            field = None

        # For some cases, the DRF init logic either breaks (custom field with internal type) or
        # the resulting field is underspecified with regards to the schema (ReadOnlyField).
        if field and isinstance(field, serializers.PrimaryKeyRelatedField):
            # special case handling only for _resolve_path_parameters() where neither queryset nor
            # parent is set by build_field. patch in queryset as _map_serializer_field requires it
            if not field.queryset:
                field.queryset = model_field.related_model.objects.none()
            return self._map_serializer_field(field, direction)
        elif field and not anyisinstance(field, [serializers.ReadOnlyField, serializers.ModelField]):
            return self._map_serializer_field(field, direction)
        elif isinstance(model_field, models.ForeignKey):
            return self._map_model_field(model_field.target_field, direction)
        elif hasattr(models, 'JSONField') and isinstance(model_field, models.JSONField):
            # fix for DRF==3.11 with django>=3.1 as it is not yet represented in the field_mapping
            return build_basic_type(OpenApiTypes.OBJECT)
        elif hasattr(models, model_field.get_internal_type()):
            # be graceful when the model field is not explicitly mapped to a serializer
            internal_type = getattr(models, model_field.get_internal_type())
            field_cls = serializers.ModelSerializer.serializer_field_mapping.get(internal_type)
            if not field_cls:
                warn(
                    f'model field "{model_field.get_internal_type()}" has no mapping in '
                    f'ModelSerializer. it may be a deprecated field. defaulting to "string"'
                )
                return build_basic_type(OpenApiTypes.STR)
            return self._map_serializer_field(field_cls(), direction)
        else:
            error(
                f'could not resolve model field "{model_field}". failed to resolve through '
                f'serializer_field_mapping, get_internal_type(), or any override mechanism. '
                f'defaulting to "string"'
            )
            return build_basic_type(OpenApiTypes.STR)