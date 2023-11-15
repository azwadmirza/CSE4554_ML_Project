    def as_create_delta(
        self,
        schema: s_schema.Schema,
        *,
        view_name: Optional[s_name.QualName] = None,
        attrs: Optional[Dict[str, Any]] = None,
    ) -> sd.Command:

        type_id, name = get_union_type_id(
            schema,
            self.components,
            opaque=self.opaque,
            module=self.module,
        )

        cmd = CreateUnionType(classname=name)
        cmd.set_attribute_value('id', type_id)
        cmd.set_attribute_value('name', name)
        cmd.set_attribute_value('components', tuple(self.components))
        cmd.set_attribute_value('is_opaque_union', self.opaque)
        return cmd