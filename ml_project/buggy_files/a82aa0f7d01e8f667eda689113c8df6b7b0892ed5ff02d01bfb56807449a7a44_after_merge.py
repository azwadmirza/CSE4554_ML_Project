    def as_create_delta(
        self,
        schema: s_schema.Schema,
        *,
        view_name: Optional[s_name.QualName] = None,
        attrs: Optional[Dict[str, Any]] = None,
    ) -> sd.CommandGroup:
        ca: Union[CreateArray, CreateArrayExprAlias]
        cmd = sd.CommandGroup()
        if view_name is None:
            ca = CreateArray(
                classname=self.get_name(schema),
                if_not_exists=True,
            )
            ca.set_attribute_value('id', self.get_id(schema))
        else:
            ca = CreateArrayExprAlias(
                classname=view_name,
            )

        el = self.subtype
        if (isinstance(el, CollectionTypeShell)
                and schema.get_by_id(el.get_id(schema), None) is None):
            cmd.add(el.as_create_delta(schema))

        ca.set_attribute_value('name', ca.classname)
        ca.set_attribute_value('element_type', el)
        ca.set_attribute_value('is_persistent', True)
        ca.set_attribute_value('dimensions', self.typemods[0])

        if attrs:
            for k, v in attrs.items():
                ca.set_attribute_value(k, v)

        cmd.add(ca)

        return cmd