    def _process_create_or_alter_ast(
        self,
        schema: s_schema.Schema,
        astnode: qlast.CreateConcretePointer,
        context: sd.CommandContext,
    ) -> None:
        """Handle the CREATE {PROPERTY|LINK} AST node.

        This may be called in the context of either Create or Alter.
        """
        if astnode.is_required is not None:
            self.set_attribute_value(
                'required',
                astnode.is_required,
                source_context=astnode.context,
            )

        if astnode.cardinality is not None:
            if isinstance(self, sd.CreateObject):
                self.set_attribute_value(
                    'cardinality',
                    astnode.cardinality,
                    source_context=astnode.context,
                )
            else:
                handler = sd.get_special_field_alter_handler_for_context(
                    'cardinality', context)
                assert handler is not None
                set_field = qlast.SetField(
                    name='cardinality',
                    value=qlast.StringConstant.from_python(
                        str(astnode.cardinality),
                    ),
                    special_syntax=True,
                    context=astnode.context,
                )
                apc = handler._cmd_tree_from_ast(schema, set_field, context)
                self.add(apc)

        parent_ctx = self.get_referrer_context_or_die(context)
        source_name = context.get_referrer_name(parent_ctx)
        self.set_attribute_value('source', so.ObjectShell(name=source_name))

        # FIXME: this is an approximate solution
        targets = qlast.get_targets(astnode.target)
        target_ref: Union[None, s_types.TypeShell, ComputableRef]

        if len(targets) > 1:
            assert isinstance(source_name, sn.QualName)

            new_targets = [
                utils.ast_to_type_shell(
                    t,
                    modaliases=context.modaliases,
                    schema=schema,
                )
                for t in targets
            ]

            target_ref = s_types.UnionTypeShell(
                components=new_targets,
                module=source_name.module,
            )
        elif targets:
            target_expr = targets[0]
            if isinstance(target_expr, qlast.TypeName):
                target_ref = utils.ast_to_type_shell(
                    target_expr,
                    modaliases=context.modaliases,
                    schema=schema,
                )
            else:
                # computable
                qlcompiler.normalize(
                    target_expr,
                    schema=schema,
                    modaliases=context.modaliases
                )
                target_ref = ComputableRef(target_expr)
        else:
            # Target is inherited.
            target_ref = None

        if isinstance(self, sd.CreateObject):
            assert astnode.target is not None
            self.set_attribute_value(
                'target',
                target_ref,
                source_context=astnode.target.context,
            )

        elif target_ref is not None:
            assert astnode.target is not None
            self.set_attribute_value(
                'target',
                target_ref,
                source_context=astnode.target.context,
            )