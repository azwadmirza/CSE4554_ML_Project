    def _canonicalize(
        self,
        schema: s_schema.Schema,
        context: CommandContext,
        scls: so.Object,
    ) -> None:
        mcls = self.get_schema_metaclass()

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
                self.add(self.init_rename_branch(
                    ref,
                    new_ref_name,
                    schema=schema,
                    context=context,
                ))