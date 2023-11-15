    def get_field_lookup_exact_type(self, api: TypeChecker, field: Union[Field, ForeignObjectRel]) -> MypyType:
        if isinstance(field, (RelatedField, ForeignObjectRel)):
            related_model_cls = field.related_model
            primary_key_field = self.get_primary_key_field(related_model_cls)
            primary_key_type = self.get_field_get_type(api, primary_key_field, method='init')

            rel_model_info = helpers.lookup_class_typeinfo(api, related_model_cls)
            if rel_model_info is None:
                return AnyType(TypeOfAny.explicit)

            model_and_primary_key_type = UnionType.make_union([Instance(rel_model_info, []), primary_key_type])
            return helpers.make_optional(model_and_primary_key_type)

        field_info = helpers.lookup_class_typeinfo(api, field.__class__)
        if field_info is None:
            return AnyType(TypeOfAny.explicit)
        return helpers.get_private_descriptor_type(field_info, '_pyi_lookup_exact_type',
                                                   is_nullable=field.null)