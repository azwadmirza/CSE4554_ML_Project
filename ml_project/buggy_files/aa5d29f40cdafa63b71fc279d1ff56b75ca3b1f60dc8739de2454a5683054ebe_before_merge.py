    def _resolve_field_from_parts(self, field_parts: Iterable[str], model_cls: Type[Model]) -> Field:
        currently_observed_model = model_cls
        field = None
        for field_part in field_parts:
            if field_part == 'pk':
                field = self.get_primary_key_field(currently_observed_model)
                continue

            field = currently_observed_model._meta.get_field(field_part)
            if isinstance(field, RelatedField):
                currently_observed_model = field.related_model
                model_name = currently_observed_model._meta.model_name
                if (model_name is not None
                        and field_part == (model_name + '_id')):
                    field = self.get_primary_key_field(currently_observed_model)

            if isinstance(field, ForeignObjectRel):
                currently_observed_model = field.related_model

        assert field is not None
        return field