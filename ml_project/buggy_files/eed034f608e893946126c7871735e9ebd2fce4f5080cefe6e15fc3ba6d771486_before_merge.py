    def _create_begin(
        self,
        schema: s_schema.Schema,
        context: sd.CommandContext,
    ) -> s_schema.Schema:
        referrer_ctx = self.get_referrer_context(context)
        if referrer_ctx is None:
            return super()._create_begin(schema, context)

        subject = referrer_ctx.scls
        assert isinstance(subject, ConsistencySubject)
        if not subject.can_accept_constraints(schema):
            raise errors.UnsupportedFeatureError(
                f'constraints cannot be defined on '
                f'{subject.get_verbosename(schema)}',
                context=self.source_context,
            )

        if not context.canonical:
            props = self.get_resolved_attributes(schema, context)
            props.pop('name')
            props.pop('subject', None)
            fullname = self.classname
            shortname = sn.shortname_from_fullname(fullname)
            constr_base, attrs, inh = Constraint.get_concrete_constraint_attrs(
                schema,
                subject,
                name=shortname,
                sourcectx=self.source_context,
                **props)

            for k, v in attrs.items():
                inherited = inh.get(k)
                self.set_attribute_value(k, v, inherited=bool(inherited))

            self.set_attribute_value('subject', subject)

        return super()._create_begin(schema, context)