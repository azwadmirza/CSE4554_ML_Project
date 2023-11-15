    def get_field_get_type(self, api: TypeChecker, field: Field, *, method: str) -> MypyType:
        """ Get a type of __get__ for this specific Django field. """
        field_info = helpers.lookup_class_typeinfo(api, field.__class__)
        if field_info is None:
            return AnyType(TypeOfAny.unannotated)

        is_nullable = self.get_field_nullability(field, method)
        if isinstance(field, RelatedField):
            related_model_cls = self.get_field_related_model_cls(field)

            if method == 'values':
                primary_key_field = self.get_primary_key_field(related_model_cls)
                return self.get_field_get_type(api, primary_key_field, method=method)

            model_info = helpers.lookup_class_typeinfo(api, related_model_cls)
            if model_info is None:
                return AnyType(TypeOfAny.unannotated)

            return Instance(model_info, [])
        else:
            return helpers.get_private_descriptor_type(field_info, '_pyi_private_get_type',
                                                       is_nullable=is_nullable)