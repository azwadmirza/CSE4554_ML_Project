def _process_view(
    *,
    stype: s_objtypes.ObjectType,
    path_id: irast.PathId,
    path_id_namespace: Optional[irast.WeakNamespace] = None,
    elements: List[qlast.ShapeElement],
    view_rptr: Optional[context.ViewRPtr] = None,
    view_name: Optional[sn.SchemaName] = None,
    is_insert: bool = False,
    is_update: bool = False,
    is_delete: bool = False,
    parser_context: pctx.ParserContext,
    ctx: context.ContextLevel,
) -> s_objtypes.ObjectType:

    if (view_name is None and ctx.env.options.schema_view_mode
            and view_rptr is not None):
        # Make sure persistent schema expression aliases have properly formed
        # names as opposed to the usual mangled form of the ephemeral
        # aliases.  This is needed for introspection readability, as well
        # as helps in maintaining proper type names for schema
        # representations that require alphanumeric names, such as
        # GraphQL.
        #
        # We use the name of the source together with the name
        # of the inbound link to form the name, so in e.g.
        #    CREATE ALIAS V := (SELECT Foo { bar: { baz: { ... } })
        # The name of the innermost alias would be "__V__bar__baz".
        source_name = view_rptr.source.get_name(ctx.env.schema).name
        if not source_name.startswith('__'):
            source_name = f'__{source_name}'
        if view_rptr.ptrcls_name is not None:
            ptr_name = view_rptr.ptrcls_name.name
        elif view_rptr.ptrcls is not None:
            ptr_name = view_rptr.ptrcls.get_shortname(ctx.env.schema).name
        else:
            raise errors.InternalServerError(
                '_process_view in schema mode received view_rptr with '
                'neither ptrcls_name, not ptrcls'
            )

        name = f'{source_name}__{ptr_name}'
        view_name = sn.Name(
            module=ctx.derived_target_module or '__derived__',
            name=name,
        )

    view_scls = schemactx.derive_view(
        stype,
        is_insert=is_insert,
        is_update=is_update,
        is_delete=is_delete,
        derived_name=view_name,
        ctx=ctx,
    )
    assert isinstance(view_scls, s_objtypes.ObjectType), view_scls
    is_mutation = is_insert or is_update
    is_defining_shape = ctx.expr_exposed or is_mutation

    if view_rptr is not None and view_rptr.ptrcls is None:
        derive_ptrcls(
            view_rptr, target_scls=view_scls,
            transparent=True, ctx=ctx)

    pointers = []

    for shape_el in elements:
        with ctx.newscope(fenced=True) as scopectx:
            pointer = _normalize_view_ptr_expr(
                shape_el, view_scls, path_id=path_id,
                path_id_namespace=path_id_namespace,
                is_insert=is_insert, is_update=is_update,
                view_rptr=view_rptr,
                ctx=scopectx)

            if pointer in pointers:
                schema = ctx.env.schema
                vnp = pointer.get_verbosename(schema, with_parent=True)

                raise errors.QueryError(
                    f'duplicate definition of {vnp}',
                    context=shape_el.context)

            pointers.append(pointer)

    if is_insert:
        explicit_ptrs = {
            ptrcls.get_shortname(ctx.env.schema).name
            for ptrcls in pointers
        }
        scls_pointers = stype.get_pointers(ctx.env.schema)
        for pn, ptrcls in scls_pointers.items(ctx.env.schema):
            if (pn in explicit_ptrs or
                    ptrcls.is_pure_computable(ctx.env.schema)):
                continue

            default_expr = ptrcls.get_default(ctx.env.schema)
            if not default_expr:
                if ptrcls.get_required(ctx.env.schema):
                    if ptrcls.is_property(ctx.env.schema):
                        # If the target is a sequence, there's no need
                        # for an explicit value.
                        ptrcls_target = ptrcls.get_target(ctx.env.schema)
                        assert ptrcls_target is not None
                        if ptrcls_target.issubclass(
                                ctx.env.schema,
                                ctx.env.schema.get('std::sequence')):
                            continue

                        what = 'property'
                    else:
                        what = 'link'
                    raise errors.MissingRequiredError(
                        f'missing value for required {what} '
                        f'{stype.get_displayname(ctx.env.schema)}.'
                        f'{ptrcls.get_displayname(ctx.env.schema)}')
                else:
                    continue

            ptrcls_sn = ptrcls.get_shortname(ctx.env.schema)
            default_ql = qlast.ShapeElement(
                expr=qlast.Path(
                    steps=[
                        qlast.Ptr(
                            ptr=qlast.ObjectRef(
                                name=ptrcls_sn.name,
                                module=ptrcls_sn.module,
                            ),
                        ),
                    ],
                ),
                compexpr=qlast.DetachedExpr(
                    expr=default_expr.qlast,
                ),
            )

            with ctx.newscope(fenced=True) as scopectx:
                pointers.append(
                    _normalize_view_ptr_expr(
                        default_ql,
                        view_scls,
                        path_id=path_id,
                        path_id_namespace=path_id_namespace,
                        is_insert=is_insert,
                        is_update=is_update,
                        from_default=True,
                        view_rptr=view_rptr,
                        ctx=scopectx,
                    ),
                )

    elif (
        stype.get_name(ctx.env.schema).module == 'schema'
        and ctx.env.options.introspection_schema_rewrites
    ):
        explicit_ptrs = {
            ptrcls.get_shortname(ctx.env.schema).name
            for ptrcls in pointers
        }
        scls_pointers = stype.get_pointers(ctx.env.schema)
        for pn, ptrcls in scls_pointers.items(ctx.env.schema):
            if (
                pn in explicit_ptrs
                or ptrcls.is_pure_computable(ctx.env.schema)
            ):
                continue

            schema_deflt = ptrcls.get_schema_reflection_default(ctx.env.schema)
            if schema_deflt is None:
                continue

            with ctx.newscope(fenced=True) as scopectx:
                implicit_ql = qlast.ShapeElement(
                    expr=qlast.Path(
                        steps=[
                            qlast.Ptr(
                                ptr=qlast.ObjectRef(
                                    name=pn,
                                ),
                            ),
                        ],
                    ),
                    compexpr=qlast.BinOp(
                        left=qlast.Path(
                            partial=True,
                            steps=[
                                qlast.Ptr(
                                    ptr=qlast.ObjectRef(name=pn),
                                    direction=(
                                        s_pointers.PointerDirection.Outbound
                                    ),
                                )
                            ],
                        ),
                        right=qlparser.parse_fragment(schema_deflt),
                        op='??',
                    ),
                )

                # Note: we only need to record the schema default
                # as a computable, but not include it in the type
                # shape, so we ignore the return value.
                _normalize_view_ptr_expr(
                    implicit_ql,
                    view_scls,
                    path_id=path_id,
                    path_id_namespace=path_id_namespace,
                    is_insert=is_insert,
                    is_update=is_update,
                    view_rptr=view_rptr,
                    ctx=scopectx,
                )

    for ptrcls in pointers:
        source: Union[s_types.Type, s_pointers.PointerLike]

        if ptrcls.is_link_property(ctx.env.schema):
            assert view_rptr is not None and view_rptr.ptrcls is not None
            source = view_rptr.ptrcls
        else:
            source = view_scls

        if is_defining_shape:
            cinfo = ctx.source_map.get(ptrcls)
            if cinfo is not None:
                shape_op = cinfo.shape_op
            else:
                shape_op = qlast.ShapeOp.ASSIGN

            ctx.env.view_shapes[source].append((ptrcls, shape_op))

    if (view_rptr is not None and view_rptr.ptrcls is not None and
            view_scls is not stype):
        ctx.env.schema = view_scls.set_field_value(
            ctx.env.schema, 'rptr', view_rptr.ptrcls)

    return view_scls