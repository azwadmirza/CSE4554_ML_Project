    def get_expected_types(self, api: TypeChecker, model_cls: Type[Model], *, method: str) -> Dict[str, MypyType]:
        from django.contrib.contenttypes.fields import GenericForeignKey

        expected_types = {}
        # add pk if not abstract=True
        if not model_cls._meta.abstract:
            primary_key_field = self.get_primary_key_field(model_cls)
            field_set_type = self.get_field_set_type(api, primary_key_field, method=method)
            expected_types['pk'] = field_set_type

        for field in model_cls._meta.get_fields():
            if isinstance(field, Field):
                field_name = field.attname
                field_set_type = self.get_field_set_type(api, field, method=method)
                expected_types[field_name] = field_set_type

                if isinstance(field, ForeignKey):
                    field_name = field.name
                    foreign_key_info = helpers.lookup_class_typeinfo(api, field.__class__)
                    if foreign_key_info is None:
                        # maybe there's no type annotation for the field
                        expected_types[field_name] = AnyType(TypeOfAny.unannotated)
                        continue

                    related_model = self.get_field_related_model_cls(field)
                    if related_model._meta.proxy_for_model is not None:
                        related_model = related_model._meta.proxy_for_model

                    related_model_info = helpers.lookup_class_typeinfo(api, related_model)
                    if related_model_info is None:
                        expected_types[field_name] = AnyType(TypeOfAny.unannotated)
                        continue

                    is_nullable = self.get_field_nullability(field, method)
                    foreign_key_set_type = helpers.get_private_descriptor_type(foreign_key_info,
                                                                               '_pyi_private_set_type',
                                                                               is_nullable=is_nullable)
                    model_set_type = helpers.convert_any_to_type(foreign_key_set_type,
                                                                 Instance(related_model_info, []))

                    expected_types[field_name] = model_set_type

            elif isinstance(field, GenericForeignKey):
                # it's generic, so cannot set specific model
                field_name = field.name
                gfk_info = helpers.lookup_class_typeinfo(api, field.__class__)
                gfk_set_type = helpers.get_private_descriptor_type(gfk_info, '_pyi_private_set_type',
                                                                   is_nullable=True)
                expected_types[field_name] = gfk_set_type

        return expected_types