    def _canonicalize(
        self,
        schema: s_schema.Schema,
        context: sd.CommandContext,
        scls: so.Object,
    ) -> None:
        super()._canonicalize(schema, context, scls)

        assert isinstance(scls, CallableObject)
        # Don't do anything for concrete constraints
        if not isinstance(scls, Function) and not scls.get_abstract(schema):
            return

        # params don't get picked up by the base _canonicalize because
        # they aren't RefDicts (and use a different mangling scheme to
        # boot), so we need to do it ourselves.
        param_list = scls.get_params(schema)
        params = CallableCommand._get_param_desc_from_params_ast(
            schema, context.modaliases, param_list.get_ast(schema))

        assert isinstance(self.new_name, sn.QualName)
        for dparam, oparam in zip(params, param_list.objects(schema)):
            self.add(self.init_rename_branch(
                oparam,
                dparam.get_fqname(schema, self.new_name),
                schema=schema,
                context=context,
            ))