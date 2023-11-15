    def _handle_alias_op(
        self,
        expr: s_expr.Expression,
        classname: sn.QualName,
        schema: s_schema.Schema,
        context: sd.CommandContext,
        is_alter: bool = False,
    ) -> Tuple[sd.Command, sd.ObjectCommand[Alias]]:
        from . import ordering as s_ordering

        ir = self._compile_alias_expr(expr.qlast, classname, schema, context)
        new_schema = ir.schema
        expr = s_expr.Expression.from_ir(expr, ir, schema=schema)

        coll_expr_aliases: List[s_types.Collection] = []
        prev_coll_expr_aliases: List[s_types.Collection] = []
        expr_aliases: List[s_types.Type] = []
        prev_expr_aliases: List[s_types.Type] = []
        prev_ir: Optional[irast.Statement] = None
        old_schema: Optional[s_schema.Schema] = None

        for vt in ir.views.values():
            if isinstance(vt, s_types.Collection):
                coll_expr_aliases.append(vt)
            else:
                new_schema = vt.set_field_value(
                    new_schema, 'alias_is_persistent', True)

                expr_aliases.append(vt)

        if is_alter:
            prev = cast(s_types.Type, schema.get(classname))
            prev_expr = prev.get_expr(schema)
            assert prev_expr is not None
            prev_ir = self._compile_alias_expr(
                prev_expr.qlast, classname, schema, context)
            old_schema = prev_ir.schema
            for vt in prev_ir.views.values():
                if isinstance(vt, s_types.Collection):
                    prev_coll_expr_aliases.append(vt)
                else:
                    prev_expr_aliases.append(vt)

        derived_delta = sd.DeltaRoot()

        for ref in ir.new_coll_types:
            colltype_shell = ref.as_shell(new_schema)
            # not "new_schema", because that already contains this
            # collection type.
            derived_delta.add(colltype_shell.as_create_delta(schema))

        if is_alter:
            assert old_schema is not None
            derived_delta.add(
                sd.delta_objects(
                    prev_expr_aliases,
                    expr_aliases,
                    sclass=s_types.Type,
                    old_schema=old_schema,
                    new_schema=new_schema,
                    context=so.ComparisonContext(),
                )
            )
        else:
            for expr_alias in expr_aliases:
                derived_delta.add(
                    expr_alias.as_create_delta(
                        schema=new_schema,
                        context=so.ComparisonContext(),
                    )
                )

        if prev_ir is not None:
            assert old_schema
            for vt in prev_coll_expr_aliases:
                dt = vt.as_colltype_delete_delta(
                    old_schema,
                    expiring_refs={self.scls},
                    view_name=classname,
                )
                derived_delta.prepend(dt)
            for vt in prev_ir.new_coll_types:
                dt = vt.as_colltype_delete_delta(
                    old_schema,
                    expiring_refs={self.scls},
                    if_exists=True,
                )
                derived_delta.prepend(dt)

        for vt in coll_expr_aliases:
            new_schema = vt.set_field_value(new_schema, 'expr', expr)
            new_schema = vt.set_field_value(
                new_schema, 'alias_is_persistent', True)
            ct = vt.as_shell(new_schema).as_create_delta(
                # not "new_schema", to ensure the nested collection types
                # are picked up properly.
                schema,
                view_name=classname,
                attrs={
                    'expr': expr,
                    'alias_is_persistent': True,
                    'expr_type': s_types.ExprType.Select,
                },
            )
            derived_delta.add(ct)

        derived_delta = s_ordering.linearize_delta(
            derived_delta, old_schema=schema, new_schema=new_schema)

        real_cmd: Optional[sd.ObjectCommand[Alias]] = None
        for op in derived_delta.get_subcommands():
            assert isinstance(op, sd.ObjectCommand)
            if (
                op.classname == classname
                and not isinstance(op, sd.DeleteObject)
            ):
                real_cmd = op
                break

        if real_cmd is None:
            assert is_alter
            for expr_alias in expr_aliases:
                if expr_alias.get_name(new_schema) == classname:
                    real_cmd = expr_alias.init_delta_command(
                        new_schema,
                        sd.AlterObject,
                    )
                    derived_delta.add(real_cmd)
                    break
            else:
                raise RuntimeError(
                    'view delta does not contain the expected '
                    'view Create/Alter command')

        real_cmd.set_attribute_value('expr', expr)

        result = sd.CommandGroup()
        result.update(derived_delta.get_subcommands())
        return result, real_cmd