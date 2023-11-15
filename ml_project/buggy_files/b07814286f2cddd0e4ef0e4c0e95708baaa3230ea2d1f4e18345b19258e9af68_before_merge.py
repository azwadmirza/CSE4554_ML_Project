    def as_create_delta(
        self,
        schema: s_schema.Schema,
        *,
        view_name: Optional[s_name.QualName] = None,
        attrs: Optional[Dict[str, Any]] = None,
    ) -> sd.CommandGroup:
        ct: Union[CreateTuple, CreateTupleExprAlias]
        cmd = sd.CommandGroup()
        type_id = self.get_id(schema)
        if view_name is None:
            ct = CreateTuple(
                classname=self.get_name(schema),
                if_not_exists=True,
            )
        else:
            ct = CreateTupleExprAlias(
                classname=view_name,
            )

        for el in self.subtypes.values():
            if (isinstance(el, CollectionTypeShell)
                    and schema.get_by_id(el.get_id(schema), None) is None):
                cmd.add(el.as_create_delta(schema))

        named = self.is_named()
        ct.set_attribute_value('id', type_id)
        ct.set_attribute_value('name', ct.classname)
        ct.set_attribute_value('named', named)
        ct.set_attribute_value('is_persistent', True)
        ct.set_attribute_value('element_types', self.subtypes)

        if attrs:
            for k, v in attrs.items():
                ct.set_attribute_value(k, v)

        cmd.add(ct)

        return cmd