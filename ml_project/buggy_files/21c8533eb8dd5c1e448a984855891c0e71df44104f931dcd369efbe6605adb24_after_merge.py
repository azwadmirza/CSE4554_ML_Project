def _normalize_view_ptr_expr(
        shape_el: qlast.ShapeElement,
        view_scls: s_objtypes.ObjectType, *,
        path_id: irast.PathId,
        path_id_namespace: Optional[irast.WeakNamespace]=None,
        is_insert: bool=False,
        is_update: bool=False,
        from_default: bool=False,
        view_rptr: Optional[context.ViewRPtr]=None,
        ctx: context.ContextLevel) -> s_pointers.Pointer:
    steps = shape_el.expr.steps
    is_linkprop = False
    is_polymorphic = False
    is_mutation = is_insert or is_update
    # Pointers may be qualified by the explicit source
    # class, which is equivalent to Expr[IS Type].
    plen = len(steps)
    ptrsource: s_sources.Source = view_scls
    qlexpr: Optional[qlast.Expr] = None
    target_typexpr = None
    source: qlast.Base
    base_ptrcls_is_alias = False

    if plen >= 2 and isinstance(steps[-1], qlast.TypeIntersection):
        # Target type intersection: foo: Type
        target_typexpr = steps[-1].type
        plen -= 1
        steps = steps[:-1]

    if plen == 1:
        # regular shape
        lexpr = steps[0]
        assert isinstance(lexpr, qlast.Ptr)
        is_linkprop = lexpr.type == 'property'
        if is_linkprop:
            if view_rptr is None or view_rptr.ptrcls is None:
                raise errors.QueryError(
                    'invalid reference to link property '
                    'in top level shape', context=lexpr.context)
            assert isinstance(view_rptr.ptrcls, s_links.Link)
            ptrsource = view_rptr.ptrcls
        source = qlast.Source()
    elif plen == 2 and isinstance(steps[0], qlast.TypeIntersection):
        # Source type intersection: [IS Type].foo
        source = qlast.Path(steps=[
            qlast.Source(),
            steps[0],
        ])
        lexpr = steps[1]
        ptype = steps[0].type
        if not isinstance(ptype, qlast.TypeName):
            raise errors.QueryError(
                'complex type expressions are not supported here',
                context=ptype.context,
            )
        source_spec = schemactx.get_schema_type(ptype.maintype, ctx=ctx)
        if not isinstance(source_spec, s_objtypes.ObjectType):
            raise errors.QueryError(
                f'expected object type, got '
                f'{source_spec.get_verbosename(ctx.env.schema)}',
                context=ptype.context,
            )
        ptrsource = source_spec
        is_polymorphic = True
    else:  # pragma: no cover
        raise RuntimeError(
            f'unexpected path length in view shape: {len(steps)}')

    assert isinstance(lexpr, qlast.Ptr)
    ptrname = lexpr.ptr.name

    compexpr: Optional[qlast.Expr] = shape_el.compexpr
    if compexpr is None and is_insert and shape_el.elements:
        # Short shape form in INSERT, e.g
        #     INSERT Foo { bar: Spam { name := 'name' }}
        # is prohibited.
        raise errors.EdgeQLSyntaxError(
            "unexpected ':'", context=steps[-1].context)

    ptrcls: Optional[s_pointers.Pointer]

    if compexpr is None:
        ptrcls = setgen.resolve_ptr(ptrsource, ptrname, ctx=ctx)
        if is_polymorphic:
            ptrcls = schemactx.derive_ptr(
                ptrcls, view_scls,
                is_insert=is_insert,
                is_update=is_update,
                ctx=ctx)

        base_ptrcls = ptrcls.get_bases(ctx.env.schema).first(ctx.env.schema)
        base_ptr_is_computable = base_ptrcls in ctx.source_map
        ptr_name = sn.Name(
            module='__',
            name=ptrcls.get_shortname(ctx.env.schema).name,
        )

        base_cardinality = base_ptrcls.get_cardinality(ctx.env.schema)
        base_is_singleton = base_cardinality is qltypes.SchemaCardinality.ONE

        if (
            shape_el.where
            or shape_el.orderby
            or shape_el.offset
            or shape_el.limit
            or base_ptr_is_computable
            or is_polymorphic
            or target_typexpr is not None
            or (ctx.implicit_limit and not base_is_singleton)
        ):

            if target_typexpr is None:
                qlexpr = qlast.Path(steps=[source, lexpr])
            else:
                qlexpr = qlast.Path(steps=[
                    source,
                    lexpr,
                    qlast.TypeIntersection(type=target_typexpr),
                ])

            qlexpr = astutils.ensure_qlstmt(qlexpr)
            assert isinstance(qlexpr, qlast.SelectQuery)
            qlexpr.where = shape_el.where
            qlexpr.orderby = shape_el.orderby

            if shape_el.offset or shape_el.limit:
                qlexpr = qlast.SelectQuery(result=qlexpr, implicit=True)
                qlexpr.offset = shape_el.offset
                qlexpr.limit = shape_el.limit

            if (
                (ctx.expr_exposed or ctx.stmt is ctx.toplevel_stmt)
                and not qlexpr.limit
                and ctx.implicit_limit
                and not base_is_singleton
            ):
                qlexpr.limit = qlast.IntegerConstant(
                    value=str(ctx.implicit_limit),
                )

        if target_typexpr is not None:
            assert isinstance(target_typexpr, qlast.TypeName)
            intersector_type = schemactx.get_schema_type(
                target_typexpr.maintype, ctx=ctx)

            int_result = schemactx.apply_intersection(
                ptrcls.get_target(ctx.env.schema),  # type: ignore
                intersector_type,
                ctx=ctx,
            )

            ptr_target = int_result.stype
        else:
            _ptr_target = ptrcls.get_target(ctx.env.schema)
            assert _ptr_target
            ptr_target = _ptr_target

        if base_ptrcls in ctx.pending_cardinality:
            # We do not know the parent's pointer cardinality yet.
            ptr_cardinality = None
            ctx.pointer_derivation_map[base_ptrcls].append(ptrcls)
            stmtctx.pend_pointer_cardinality_inference(
                ptrcls=ptrcls,
                specified_required=shape_el.required,
                specified_card=shape_el.cardinality,
                source_ctx=shape_el.context,
                ctx=ctx)
        else:
            ptr_cardinality = base_ptrcls.get_cardinality(ctx.env.schema)

        implicit_tid = has_implicit_tid(
            ptr_target,
            is_mutation=is_mutation,
            ctx=ctx,
        )

        if shape_el.elements or implicit_tid:
            sub_view_rptr = context.ViewRPtr(
                ptrsource if is_linkprop else view_scls,
                ptrcls=ptrcls,
                is_insert=is_insert,
                is_update=is_update)

            sub_path_id = pathctx.extend_path_id(
                path_id,
                ptrcls=base_ptrcls,
                ns=ctx.path_id_namespace,
                ctx=ctx)

            ctx.path_scope.attach_path(sub_path_id,
                                       context=shape_el.context)

            if not isinstance(ptr_target, s_objtypes.ObjectType):
                raise errors.QueryError(
                    f'shapes cannot be applied to '
                    f'{ptr_target.get_verbosename(ctx.env.schema)}',
                    context=shape_el.context,
                )

            if is_update:
                for subel in shape_el.elements or []:
                    is_prop = (
                        isinstance(subel.expr.steps[0], qlast.Ptr) and
                        subel.expr.steps[0].type == 'property'
                    )
                    if not is_prop:
                        raise errors.QueryError(
                            'only references to link properties are allowed '
                            'in nested UPDATE shapes', context=subel.context)

                ptr_target = _process_view(
                    stype=ptr_target, path_id=sub_path_id,
                    path_id_namespace=path_id_namespace,
                    view_rptr=sub_view_rptr,
                    elements=shape_el.elements, is_update=True,
                    parser_context=shape_el.context,
                    ctx=ctx)
            else:
                ptr_target = _process_view(
                    stype=ptr_target, path_id=sub_path_id,
                    path_id_namespace=path_id_namespace,
                    view_rptr=sub_view_rptr,
                    elements=shape_el.elements,
                    parser_context=shape_el.context,
                    ctx=ctx)

    else:
        base_ptrcls = ptrcls = None

        if (is_mutation
                and ptrname not in ctx.special_computables_in_mutation_shape):
            # If this is a mutation, the pointer must exist.
            ptrcls = setgen.resolve_ptr(ptrsource, ptrname, ctx=ctx)

            base_ptrcls = ptrcls.get_bases(
                ctx.env.schema).first(ctx.env.schema)

            ptr_name = sn.Name(
                module='__',
                name=ptrcls.get_shortname(ctx.env.schema).name,
            )

        else:
            ptr_name = sn.Name(
                module='__',
                name=ptrname,
            )

            try:
                ptrcls = setgen.resolve_ptr(
                    ptrsource,
                    ptrname,
                    track_ref=False,
                    ctx=ctx,
                )

                base_ptrcls = ptrcls.get_bases(
                    ctx.env.schema).first(ctx.env.schema)
            except errors.InvalidReferenceError:
                # This is a NEW compitable pointer, it's fine.
                pass

        qlexpr = astutils.ensure_qlstmt(compexpr)

        if ((ctx.expr_exposed or ctx.stmt is ctx.toplevel_stmt)
                and ctx.implicit_limit
                and isinstance(qlexpr, qlast.OffsetLimitMixin)
                and not qlexpr.limit):
            qlexpr.limit = qlast.IntegerConstant(value=str(ctx.implicit_limit))

        with ctx.newscope(fenced=True) as shape_expr_ctx:
            # Put current pointer class in context, so
            # that references to link properties in sub-SELECT
            # can be resolved.  This is necessary for proper
            # evaluation of link properties on computable links,
            # most importantly, in INSERT/UPDATE context.
            shape_expr_ctx.view_rptr = context.ViewRPtr(
                ptrsource if is_linkprop else view_scls,
                ptrcls=ptrcls,
                ptrcls_name=ptr_name,
                ptrcls_is_linkprop=is_linkprop,
                is_insert=is_insert,
                is_update=is_update,
            )

            shape_expr_ctx.defining_view = view_scls
            shape_expr_ctx.path_scope.unnest_fence = True
            shape_expr_ctx.partial_path_prefix = setgen.class_set(
                view_scls.get_bases(ctx.env.schema).first(ctx.env.schema),
                path_id=path_id, ctx=shape_expr_ctx)
            prefix_rptrref = path_id.rptr()
            if prefix_rptrref is not None:
                # Source path seems to contain multiple steps,
                # so set up a rptr for abbreviated link property
                # paths.
                src_path_id = path_id.src_path()
                assert src_path_id is not None
                ctx.env.schema, src_t = irtyputils.ir_typeref_to_type(
                    shape_expr_ctx.env.schema,
                    src_path_id.target,
                )
                prefix_rptr = irast.Pointer(
                    source=setgen.class_set(
                        src_t,
                        path_id=src_path_id,
                        ctx=shape_expr_ctx,
                    ),
                    target=shape_expr_ctx.partial_path_prefix,
                    ptrref=prefix_rptrref,
                    direction=s_pointers.PointerDirection.Outbound,
                )
                shape_expr_ctx.partial_path_prefix.rptr = prefix_rptr

            if is_mutation and ptrcls is not None:
                shape_expr_ctx.expr_exposed = True
                shape_expr_ctx.empty_result_type_hint = \
                    ptrcls.get_target(ctx.env.schema)

            shape_expr_ctx.stmt_metadata[qlexpr] = context.StatementMetadata(
                iterator_target=True,
            )
            irexpr = dispatch.compile(qlexpr, ctx=shape_expr_ctx)

            if (
                shape_el.operation.op is qlast.ShapeOp.APPEND
                or shape_el.operation.op is qlast.ShapeOp.SUBTRACT
            ):
                if not is_update:
                    op = (
                        '+=' if shape_el.operation.op is qlast.ShapeOp.APPEND
                        else '-='
                    )
                    raise errors.EdgeQLSyntaxError(
                        f"unexpected '{op}'",
                        context=shape_el.operation.context,
                    )

            irexpr.context = compexpr.context

            if base_ptrcls is None:
                base_ptrcls = shape_expr_ctx.view_rptr.base_ptrcls
                base_ptrcls_is_alias = shape_expr_ctx.view_rptr.ptrcls_is_alias

            if ptrcls is not None:
                ctx.env.schema = ptrcls.set_field_value(
                    ctx.env.schema, 'is_owned', True)

        ptr_cardinality = None
        ptr_target = inference.infer_type(irexpr, ctx.env)

        if (
            isinstance(ptr_target, s_types.Collection)
            and not ctx.env.orig_schema.get_by_id(ptr_target.id, default=None)
        ):
            # Record references to implicitly defined collection types,
            # so that the alias delta machinery can pick them up.
            ctx.env.created_schema_objects.add(ptr_target)

        anytype = ptr_target.find_any(ctx.env.schema)
        if anytype is not None:
            raise errors.QueryError(
                'expression returns value of indeterminate type',
                context=ctx.env.type_origins.get(anytype),
            )

        # Validate that the insert/update expression is
        # of the correct class.
        if is_mutation and ptrcls is not None:
            base_target = ptrcls.get_target(ctx.env.schema)
            assert base_target is not None
            if ptr_target.assignment_castable_to(
                    base_target,
                    schema=ctx.env.schema):
                # Force assignment casts if the target type is not a
                # subclass of the base type and the cast is not to an
                # object type.
                if not (
                    base_target.is_object_type()
                    or schemactx.is_type_compatible(
                        base_target,
                        ptr_target,
                        ctx=ctx
                    )
                ):
                    qlexpr = astutils.ensure_qlstmt(qlast.TypeCast(
                        type=typegen.type_to_ql_typeref(base_target, ctx=ctx),
                        expr=compexpr,
                    ))
                    ptr_target = base_target

            else:
                expected = [
                    repr(str(base_target.get_displayname(ctx.env.schema)))
                ]

                ercls: Type[errors.EdgeDBError]
                if ptrcls.is_property(ctx.env.schema):
                    ercls = errors.InvalidPropertyTargetError
                else:
                    ercls = errors.InvalidLinkTargetError

                ptr_vn = ptrcls.get_verbosename(ctx.env.schema,
                                                with_parent=True)

                raise ercls(
                    f'invalid target for {ptr_vn}: '
                    f'{str(ptr_target.get_displayname(ctx.env.schema))!r} '
                    f'(expecting {" or ".join(expected)})'
                )

    if qlexpr is not None or ptrcls is None:
        src_scls: s_sources.Source

        if is_linkprop:
            # Proper checking was done when is_linkprop is defined.
            assert view_rptr is not None
            assert isinstance(view_rptr.ptrcls, s_links.Link)
            src_scls = view_rptr.ptrcls
        else:
            src_scls = view_scls

        if ptr_target.is_object_type():
            base = ctx.env.get_track_schema_object('std::link')
        else:
            base = ctx.env.get_track_schema_object('std::property')

        if base_ptrcls is not None:
            derive_from = base_ptrcls
        else:
            derive_from = base

        derived_name = schemactx.derive_view_name(
            base_ptrcls,
            derived_name_base=ptr_name,
            derived_name_quals=[src_scls.get_name(ctx.env.schema)],
            ctx=ctx)

        existing: Optional[s_objects.Object] = (
            ctx.env.schema.get(derived_name, None))
        if existing is not None:
            assert isinstance(existing, s_pointers.Pointer)
            existing_target = existing.get_target(ctx.env.schema)
            assert existing_target is not None
            if ptr_target == existing_target:
                ptrcls = existing
            elif ptr_target.implicitly_castable_to(
                    existing_target, ctx.env.schema):
                ctx.env.schema = existing.set_target(
                    ctx.env.schema, ptr_target)
                ptrcls = existing
            else:
                target_rptr_set = (
                    ptr_target.get_rptr(ctx.env.schema) is not None
                )

                if target_rptr_set:
                    ctx.env.schema = ptr_target.set_field_value(
                        ctx.env.schema,
                        'rptr',
                        None,
                    )

                ctx.env.schema = existing.delete(ctx.env.schema)

                try:
                    ptrcls = schemactx.derive_ptr(
                        derive_from, src_scls, ptr_target,
                        is_insert=is_insert,
                        is_update=is_update,
                        derived_name=derived_name,
                        inheritance_merge=True,
                        ctx=ctx,
                    )
                except errors.SchemaError as e:
                    if compexpr is not None:
                        e.set_source_context(compexpr.context)
                    else:
                        e.set_source_context(shape_el.expr.steps[-1].context)
                    raise

                if target_rptr_set:
                    ctx.env.schema = ptr_target.set_field_value(
                        ctx.env.schema,
                        'rptr',
                        ptrcls,
                    )
        else:
            ptrcls = schemactx.derive_ptr(
                derive_from, src_scls, ptr_target,
                is_insert=is_insert,
                is_update=is_update,
                derived_name=derived_name,
                ctx=ctx)

    elif ptrcls.get_target(ctx.env.schema) != ptr_target:
        ctx.env.schema = ptrcls.set_target(ctx.env.schema, ptr_target)

    assert ptrcls is not None

    if qlexpr is None:
        # This is not a computable, just a pointer
        # to a nested shape.  Have it reuse the original
        # pointer name so that in `Foo.ptr.name` and
        # `Foo { ptr: {name}}` are the same path.
        path_id_name = base_ptrcls.get_name(ctx.env.schema)
        ctx.env.schema = ptrcls.set_field_value(
            ctx.env.schema, 'path_id_name', path_id_name
        )

    if qlexpr is not None:
        ctx.source_map[ptrcls] = context.ComputableInfo(
            qlexpr=qlexpr,
            context=ctx,
            path_id=path_id,
            path_id_ns=path_id_namespace,
            shape_op=shape_el.operation.op,
        )

    if compexpr is not None or is_polymorphic:
        ctx.env.schema = ptrcls.set_field_value(
            ctx.env.schema,
            'computable',
            True,
        )

        ctx.env.schema = ptrcls.set_field_value(
            ctx.env.schema,
            'is_owned',
            True,
        )

    if ptr_cardinality is not None:
        ctx.env.schema = ptrcls.set_field_value(
            ctx.env.schema, 'cardinality', ptr_cardinality)
    else:
        if qlexpr is None and ptrcls is not base_ptrcls:
            ctx.pointer_derivation_map[base_ptrcls].append(ptrcls)

        base_cardinality = None
        base_required = False
        if base_ptrcls is not None and not base_ptrcls_is_alias:
            base_cardinality = base_ptrcls.get_cardinality(ctx.env.schema)
            base_required = base_ptrcls.get_required(ctx.env.schema)

        if base_cardinality is None:
            specified_cardinality = shape_el.cardinality
            specified_required = shape_el.required
        else:
            specified_cardinality = base_cardinality
            specified_required = base_required

            if (shape_el.cardinality is not None
                    and base_ptrcls is not None
                    and shape_el.cardinality != base_cardinality):
                base_src = base_ptrcls.get_source(ctx.env.schema)
                assert base_src is not None
                base_src_name = base_src.get_verbosename(ctx.env.schema)
                raise errors.SchemaError(
                    f'cannot redefine the cardinality of '
                    f'{ptrcls.get_verbosename(ctx.env.schema)}: '
                    f'it is defined as {base_cardinality.as_ptr_qual()!r} '
                    f'in the base {base_src_name}',
                    context=compexpr and compexpr.context,
                )
            # The required flag may be inherited from the base
            specified_required = shape_el.required or base_required

        stmtctx.pend_pointer_cardinality_inference(
            ptrcls=ptrcls,
            specified_required=specified_required,
            specified_card=specified_cardinality,
            is_mut_assignment=is_mutation,
            shape_op=shape_el.operation.op,
            source_ctx=shape_el.context,
            ctx=ctx,
        )

        ctx.env.schema = ptrcls.set_field_value(
            ctx.env.schema, 'cardinality', None)

    if (
        ptrcls.is_protected_pointer(ctx.env.schema)
        and qlexpr is not None
        and not from_default
        and not ctx.env.options.allow_writing_protected_pointers
    ):
        ptrcls_sn = ptrcls.get_shortname(ctx.env.schema)
        if is_polymorphic:
            msg = (f'cannot access {ptrcls_sn.name} on a polymorphic '
                   f'shape element')
        else:
            msg = f'cannot assign to {ptrcls_sn.name}'
        raise errors.QueryError(msg, context=shape_el.context)

    if is_update and ptrcls.get_readonly(ctx.env.schema):
        raise errors.QueryError(
            f'cannot update {ptrcls.get_verbosename(ctx.env.schema)}: '
            f'it is declared as read-only',
            context=compexpr and compexpr.context,
        )

    return ptrcls