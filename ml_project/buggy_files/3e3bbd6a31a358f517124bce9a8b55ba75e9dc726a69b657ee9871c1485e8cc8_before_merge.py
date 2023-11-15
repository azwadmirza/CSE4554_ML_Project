    def _canonicalize(
        self,
        schema: s_schema.Schema,
        context: CommandContext,
        scls: so.Object,
    ) -> Sequence[Command]:
        mcls = self.get_schema_metaclass()
        commands = []

        for refdict in mcls.get_refdicts():
            all_refs = set(
                scls.get_field_value(schema, refdict.attr).objects(schema)
            )

            ref: so.Object
            for ref in all_refs:
                ref_name = ref.get_name(schema)
                quals = list(sn.quals_from_fullname(ref_name))
                assert isinstance(self.new_name, sn.QualName)
                quals[0] = str(self.new_name)
                shortname = sn.shortname_from_fullname(ref_name)
                new_ref_name = sn.QualName(
                    name=sn.get_specialized_name(shortname, *quals),
                    module=self.new_name.module,
                )

                commands.append(self._canonicalize_ref_rename(
                    ref, ref_name, new_ref_name, schema, context, scls))

        # Record the fact that RenameObject._canonicalize
        # was called on this object to guard against possible
        # duplicate calls.
        context.store_value(('renamecanon', self), True)

        return commands