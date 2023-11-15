    def _alter_pointer_type(self, pointer, schema, orig_schema, context):
        old_ptr_stor_info = types.get_pointer_storage_info(
            pointer, schema=orig_schema)
        new_target = pointer.get_target(schema)

        ptr_table = old_ptr_stor_info.table_type == 'link'
        is_link = isinstance(pointer, s_links.Link)
        is_lprop = pointer.is_link_property(schema)
        is_multi = ptr_table and not is_lprop
        is_required = pointer.get_required(schema)
        changing_col_type = not is_link

        if is_multi:
            if isinstance(self, sd.AlterObjectFragment):
                source_op = self.get_parent_op(context)
            else:
                source_op = self
        else:
            source_ctx = self.get_referrer_context_or_die(context)
            source_op = source_ctx.op

        # Ignore type narrowing resulting from a creation of a subtype
        # as there isn't any data in the link yet.
        if is_link and isinstance(source_op, sd.CreateObject):
            return

        new_target = pointer.get_target(schema)
        orig_target = pointer.get_target(orig_schema)
        new_type = types.pg_type_from_object(
            schema, new_target, persistent_tuples=True)

        source = source_op.scls
        using_eql_expr = self.cast_expr

        # For links, when the new type is a supertype of the old, no
        # SQL-level changes are necessary, unless an explicit conversion
        # expression was specified.
        if (
            is_link
            and using_eql_expr is None
            and orig_target.issubclass(orig_schema, new_target)
        ):
            return

        if using_eql_expr is None and not is_link:
            # A lack of an explicit EdgeQL conversion expression means
            # that the new type is assignment-castable from the old type
            # in the EdgeDB schema.  BUT, it would not necessarily be
            # assignment-castable in Postgres, especially if the types are
            # compound.  Thus, generate an explicit cast expression.
            pname = pointer.get_shortname(schema).name
            using_eql_expr = s_expr.Expression.from_ast(
                ql_ast.TypeCast(
                    expr=ql_ast.Path(
                        partial=True,
                        steps=[
                            ql_ast.Ptr(
                                ptr=ql_ast.ObjectRef(name=pname),
                                type='property' if is_lprop else None,
                            ),
                        ],
                    ),
                    type=s_utils.typeref_to_ast(schema, new_target),
                ),
                schema=orig_schema,
            )

        # There are two major possibilities about the USING claus:
        # 1) trivial case, where the USING clause refers only to the
        # columns of the source table, in which case we simply compile that
        # into an equivalent SQL USING clause, and 2) complex case, which
        # supports arbitrary queries, but requires a temporary column,
        # which is populated with the transition query and then used as the
        # source for the SQL USING clause.
        using_eql_expr, using_sql_expr, orig_rel_alias, sql_expr_is_trivial = (
            self._compile_conversion_expr(
                pointer=pointer,
                conv_expr=using_eql_expr,
                schema=schema,
                orig_schema=orig_schema,
                context=context,
            )
        )

        expr_is_nullable = using_eql_expr.cardinality.can_be_zero()

        need_temp_col = (
            (is_multi and expr_is_nullable)
            or (changing_col_type and not sql_expr_is_trivial)
        )

        if changing_col_type:
            self.pgops.add(source_op.drop_inhview(
                schema,
                context,
                source,
                drop_ancestors=True,
            ))

        tab = q(*old_ptr_stor_info.table_name)
        target_col = old_ptr_stor_info.column_name
        aux_ptr_table = None
        aux_ptr_col = None

        if is_link:
            old_lb_ptr_stor_info = types.get_pointer_storage_info(
                pointer, link_bias=True, schema=orig_schema)

            if (
                old_lb_ptr_stor_info is not None
                and old_lb_ptr_stor_info.table_type == 'link'
            ):
                aux_ptr_table = old_lb_ptr_stor_info.table_name
                aux_ptr_col = old_lb_ptr_stor_info.column_name

        if not sql_expr_is_trivial:
            if need_temp_col:
                alter_table = source_op.get_alter_table(
                    schema, context, priority=0, force_new=True, manual=True)
                temp_column = dbops.Column(
                    name=f'??{pointer.id}_{common.get_unique_random_name()}',
                    type=qt(new_type),
                )
                alter_table.add_operation(
                    dbops.AlterTableAddColumn(temp_column))
                self.pgops.add(alter_table)
                target_col = temp_column.name

            if is_multi:
                obj_id_ref = f'{qi(orig_rel_alias)}.source'
            else:
                obj_id_ref = f'{qi(orig_rel_alias)}.id'

            if is_required and not is_multi:
                using_sql_expr = textwrap.dedent(f'''\
                    edgedb.raise_on_null(
                        ({using_sql_expr}),
                        'not_null_violation',
                        msg => 'missing value for required property',
                        detail => '{{"object_id": "' || {obj_id_ref} || '"}}',
                        "column" => {ql(str(pointer.id))}
                    )
                ''')

            update_qry = textwrap.dedent(f'''\
                UPDATE {tab} AS {qi(orig_rel_alias)}
                SET {qi(target_col)} = ({using_sql_expr})
            ''')

            self.pgops.add(dbops.Query(update_qry))
            actual_using_expr = qi(target_col)
        else:
            actual_using_expr = using_sql_expr

        if changing_col_type or need_temp_col:
            alter_table = source_op.get_alter_table(
                schema, context, priority=0, force_new=True, manual=True)

        if is_multi:
            # Remove all rows where the conversion expression produced NULLs.
            col = qi(target_col)
            if pointer.get_required(schema):
                clean_nulls = dbops.Query(textwrap.dedent(f'''\
                    WITH d AS (
                        DELETE FROM {tab} WHERE {col} IS NULL RETURNING source
                    )
                    SELECT
                        edgedb.raise(
                            NULL::text,
                            'not_null_violation',
                            msg => 'missing value for required property',
                            detail => '{{"object_id": "' || l.source || '"}}',
                            "column" => {ql(str(pointer.id))}
                        )
                    FROM
                        {tab} AS l
                    WHERE
                        l.source IN (SELECT source FROM d)
                        AND True = ALL (
                            SELECT {col} IS NULL
                            FROM {tab} AS l2
                            WHERE l2.source = l.source
                        )
                    LIMIT
                        1
                    INTO _dummy_text;
                '''))
            else:
                clean_nulls = dbops.Query(textwrap.dedent(f'''\
                    DELETE FROM {tab} WHERE {col} IS NULL
                '''))

            self.pgops.add(clean_nulls)

        elif aux_ptr_table is not None:
            # SINGLE links with link properties are represented in
            # _two_ tables (the host type table and a link table with
            # properties), and we must update both.
            actual_col = qi(old_ptr_stor_info.column_name)

            if expr_is_nullable and not is_required:
                cleanup_qry = textwrap.dedent(f'''\
                    DELETE FROM {q(*aux_ptr_table)} AS aux
                    USING {tab} AS main
                    WHERE
                        main.id = aux.source
                        AND {actual_col} IS NULL
                ''')
                self.pgops.add(dbops.Query(cleanup_qry))

            update_qry = textwrap.dedent(f'''\
                UPDATE {q(*aux_ptr_table)} AS aux
                SET {qi(aux_ptr_col)} = main.{actual_col}
                FROM {tab} AS main
                WHERE
                    main.id = aux.source
            ''')
            self.pgops.add(dbops.Query(update_qry))

        if changing_col_type:
            alter_type = dbops.AlterTableAlterColumnType(
                old_ptr_stor_info.column_name,
                common.quote_type(new_type),
                using_expr=actual_using_expr,
            )

            alter_table.add_operation(alter_type)
        elif need_temp_col:
            move_data = dbops.Query(textwrap.dedent(f'''\
                UPDATE
                    {q(*old_ptr_stor_info.table_name)} AS {qi(orig_rel_alias)}
                SET
                    {qi(old_ptr_stor_info.column_name)} = ({qi(target_col)})
            '''))
            self.pgops.add(move_data)

        if need_temp_col:
            alter_table.add_operation(dbops.AlterTableDropColumn(temp_column))

        if changing_col_type or need_temp_col:
            self.pgops.add(alter_table)

        if changing_col_type:
            self.schedule_inhviews_update(
                schema,
                context,
                source,
                update_descendants=True,
                update_ancestors=True,
            )