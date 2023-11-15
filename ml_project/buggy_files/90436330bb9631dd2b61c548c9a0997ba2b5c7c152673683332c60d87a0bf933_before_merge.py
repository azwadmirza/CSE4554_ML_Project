    def _canonicalize(
        self,
        schema: s_schema.Schema,
        context: sd.CommandContext,
        scls: so.Object,
    ) -> List[sd.Command]:
        assert isinstance(scls, Annotation)
        commands = list(super()._canonicalize(schema, context, scls))

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
            commands.append(
                self._canonicalize_ref_rename(
                    ref, ref_name, new_ref_name, schema, context, scls))

        return commands