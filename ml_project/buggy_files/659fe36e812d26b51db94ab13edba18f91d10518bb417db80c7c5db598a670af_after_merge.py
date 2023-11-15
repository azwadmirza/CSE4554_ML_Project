    def _canonicalize(
        self,
        schema: s_schema.Schema,
        context: sd.CommandContext,
        scls: so.Object,
    ) -> None:
        super()._canonicalize(schema, context, scls)

        assert isinstance(scls, Constraint)
        # Don't do anything for concrete constraints
        if not scls.get_abstract(schema):
            return

        # Concrete constraints are children of abstract constraints
        # and have names derived from the abstract constraints. We
        # unfortunately need to go update their names.
        children = scls.children(schema)
        for ref in children:
            if ref.get_abstract(schema):
                continue

            ref_name = ref.get_name(schema)
            quals = list(sn.quals_from_fullname(ref_name))
            new_ref_name = sn.QualName(
                name=sn.get_specialized_name(self.new_name, *quals),
                module=ref_name.module,
            )

            self.add(self.init_rename_branch(
                ref,
                new_ref_name,
                schema=schema,
                context=context,
            ))

        return