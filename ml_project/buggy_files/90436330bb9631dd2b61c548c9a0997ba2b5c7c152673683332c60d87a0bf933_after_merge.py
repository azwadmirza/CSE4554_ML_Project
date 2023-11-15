    def _canonicalize(
        self,
        schema: s_schema.Schema,
        context: sd.CommandContext,
        scls: so.Object,
    ) -> None:
        super()._canonicalize(schema, context, scls)
        assert isinstance(scls, Annotation)

        # AnnotationValues have names derived from the abstract
        # annotations. We unfortunately need to go update their names.
        annot_vals = cast(
            AbstractSet[AnnotationValue],
            schema.get_referrers(
                scls, scls_type=AnnotationValue, field_name='annotation'))

        for ref in annot_vals:
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