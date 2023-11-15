    def _canonicalize(
        self,
        schema: s_schema.Schema,
        context: sd.CommandContext,
        scls: so.Object,
    ) -> List[sd.Command]:
        assert isinstance(scls, Constraint)
        commands = list(super()._canonicalize(schema, context, scls))

        # Don't do anything for concrete constraints
        if not scls.get_abstract(schema):
            return commands

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
            commands.append(
                self._canonicalize_ref_rename(
                    ref, ref_name, new_ref_name, schema, context, scls))

        return commands