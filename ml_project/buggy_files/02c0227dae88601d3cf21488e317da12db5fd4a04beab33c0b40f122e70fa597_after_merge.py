    def run_with_model_cls(self, model_cls: Type[Model]) -> None:
        for field in model_cls._meta.get_fields():
            if isinstance(field, ForeignKey):
                related_model_cls = self.django_context.get_field_related_model_cls(field)
                if related_model_cls is None:
                    error_context: Context = self.ctx.cls
                    field_sym = self.ctx.cls.info.get(field.name)
                    if field_sym is not None and field_sym.node is not None:
                        error_context = field_sym.node
                    self.api.fail(f'Cannot find model {field.related_model!r} '
                                  f'referenced in field {field.name!r} ',
                                  ctx=error_context)
                    self.add_new_node_to_model_class(field.attname,
                                                     AnyType(TypeOfAny.explicit))
                    continue

                if related_model_cls._meta.abstract:
                    continue

                rel_primary_key_field = self.django_context.get_primary_key_field(related_model_cls)
                field_info = self.lookup_class_typeinfo_or_incomplete_defn_error(rel_primary_key_field.__class__)
                is_nullable = self.django_context.get_field_nullability(field, None)
                set_type, get_type = get_field_descriptor_types(field_info, is_nullable)
                self.add_new_node_to_model_class(field.attname,
                                                 Instance(field_info, [set_type, get_type]))