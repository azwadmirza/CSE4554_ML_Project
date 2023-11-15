    def as_create_delta(
        self: Object_T,
        schema: s_schema.Schema,
        context: ComparisonContext,
    ) -> sd.ObjectCommand[Object_T]:
        from . import delta as sd

        cls = type(self)
        delta = self.init_delta_command(
            schema,
            sd.CreateObject,
            canonical=True,
        )

        if context.generate_prompts:
            delta.set_annotation('orig_cmdclass', type(delta))

        ff = cls.get_fields(sorted=True).items()
        fields = {fn: f for fn, f in ff if f.simpledelta and not f.ephemeral}
        for fn, f in fields.items():
            value = self.get_explicit_field_value(schema, fn, None)

            if (
                value is None
                and context.descriptive_mode
                and (
                    f.describe_visibility
                    & DescribeVisibilityFlags.SHOW_IF_DERIVED
                )
            ):
                value = self.get_field_value(schema, fn)
                value_from_default = True
            else:
                value_from_default = False

            if f.aux_cmd_data:
                delta.set_object_aux_data(fn, value)
            if value is not None:
                v: Any
                if issubclass(f.type, ObjectContainer):
                    v = value.as_shell(schema)
                else:
                    v = value
                self.record_field_create_delta(
                    schema,
                    delta,
                    context=context,
                    fname=fn,
                    value=v,
                    from_default=value_from_default,
                )

        for refdict in cls.get_refdicts():
            refcoll: ObjectCollection[Object] = (
                self.get_field_value(schema, refdict.attr))
            sorted_refcoll = sorted(
                refcoll.objects(schema),
                key=lambda o: o.get_name(schema),
            )
            for ref in sorted_refcoll:
                delta.add(ref.as_create_delta(schema, context))

        return delta