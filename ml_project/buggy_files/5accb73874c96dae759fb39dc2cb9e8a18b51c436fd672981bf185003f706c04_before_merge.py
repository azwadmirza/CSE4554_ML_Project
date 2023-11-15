    def get_field_set_type(self, api: TypeChecker, field: Field, *, method: str) -> MypyType:
        """ Get a type of __set__ for this specific Django field. """
        target_field = field
        if isinstance(field, ForeignKey):
            target_field = field.target_field

        field_info = helpers.lookup_class_typeinfo(api, target_field.__class__)
        if field_info is None:
            return AnyType(TypeOfAny.from_error)

        field_set_type = helpers.get_private_descriptor_type(field_info, '_pyi_private_set_type',
                                                             is_nullable=self.get_field_nullability(field, method))
        if isinstance(target_field, ArrayField):
            argument_field_type = self.get_field_set_type(api, target_field.base_field, method=method)
            field_set_type = helpers.convert_any_to_type(field_set_type, argument_field_type)
        return field_set_type