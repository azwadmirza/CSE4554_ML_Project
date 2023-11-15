    def _create_innards(self, schema, context):
        schema = super()._create_innards(schema, context)

        referrer_ctx = self.get_referrer_context(context)
        if referrer_ctx is None:
            return schema

        referrer = referrer_ctx.scls
        referrer_cls = type(referrer)
        mcls = type(self.scls)
        refdict = referrer_cls.get_refdict_for_class(mcls)

        if refdict.backref_attr:
            # Set the back-reference on referenced object
            # to the referrer.
            schema = self.scls.set_field_value(
                schema, refdict.backref_attr, referrer)

        schema = referrer.add_classref(schema, refdict.attr, self.scls)

        if (not self.scls.get_is_final(schema)
                and isinstance(referrer, inheriting.InheritingObject)):
            if not context.canonical:
                # Propagate the creation of a new ref to descendants.
                alter_cmd = sd.ObjectCommandMeta.get_command_class_or_die(
                    sd.AlterObject, referrer_cls)

                ref_field_type = referrer_cls.get_field(refdict.attr).type
                refname = ref_field_type.get_key_for(schema, self.scls)

                if context.enable_recursion:
                    for child in referrer.children(schema):
                        alter = alter_cmd(classname=child.get_name(schema))
                        with alter.new_context(schema, context, child):
                            schema, cmd = self._propagate_ref_creation(
                                schema, context, refdict, refname, child)
                            alter.add(cmd)
                        self.add(alter)
            else:
                for op in self.get_subcommands(metaclass=referrer_cls):
                    schema, _ = op.apply(schema, context=context)

        return schema