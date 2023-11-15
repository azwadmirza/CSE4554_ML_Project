    def get_field_related_model_cls(self, field: Union[RelatedField, ForeignObjectRel]) -> Optional[Type[Model]]:
        if isinstance(field, RelatedField):
            related_model_cls = field.remote_field.model
        else:
            related_model_cls = field.field.model

        if isinstance(related_model_cls, str):
            if related_model_cls == 'self':
                # same model
                related_model_cls = field.model
            elif '.' not in related_model_cls:
                # same file model
                related_model_fullname = field.model.__module__ + '.' + related_model_cls
                related_model_cls = self.get_model_class_by_fullname(related_model_fullname)
            else:
                related_model_cls = self.apps_registry.get_model(related_model_cls)

        return related_model_cls