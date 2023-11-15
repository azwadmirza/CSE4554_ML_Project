def derive_view(
    stype: s_types.Type,
    *,
    derived_name: Optional[sn.QualName] = None,
    derived_name_quals: Optional[Sequence[str]] = (),
    derived_name_base: Optional[str] = None,
    preserve_shape: bool = False,
    preserve_path_id: bool = False,
    is_insert: bool = False,
    is_update: bool = False,
    is_delete: bool = False,
    inheritance_merge: bool = True,
    attrs: Optional[Dict[str, Any]] = None,
    ctx: context.ContextLevel,
) -> s_types.Type:

    if derived_name is None:
        assert isinstance(stype, s_obj.DerivableObject)
        derived_name = derive_view_name(
            stype=stype, derived_name_quals=derived_name_quals,
            derived_name_base=derived_name_base, ctx=ctx)

    if is_insert:
        exprtype = s_types.ExprType.Insert
    elif is_update:
        exprtype = s_types.ExprType.Update
    elif is_delete:
        exprtype = s_types.ExprType.Delete
    else:
        exprtype = s_types.ExprType.Select

    if attrs is None:
        attrs = {}
    else:
        attrs = dict(attrs)

    attrs['expr_type'] = exprtype

    derived: s_types.Type

    if isinstance(stype, s_abc.Collection):
        ctx.env.schema, derived = stype.derive_subtype(
            ctx.env.schema, name=derived_name)

    elif isinstance(stype, s_obj.DerivableInheritingObject):
        ctx.env.schema, derived = stype.derive_subtype(
            ctx.env.schema,
            name=derived_name,
            inheritance_merge=inheritance_merge,
            inheritance_refdicts={'pointers'},
            mark_derived=True,
            transient=True,
            preserve_path_id=preserve_path_id,
            attrs=attrs,
        )

        if (not stype.generic(ctx.env.schema)
                and isinstance(derived, s_sources.Source)):
            scls_pointers = stype.get_pointers(ctx.env.schema)
            derived_own_pointers = derived.get_pointers(ctx.env.schema)

            for pn, ptr in derived_own_pointers.items(ctx.env.schema):
                # This is a view of a view.  Make sure query-level
                # computable expressions for pointers are carried over.
                src_ptr = scls_pointers.get(ctx.env.schema, pn)
                computable_data = ctx.source_map.get(src_ptr)
                if computable_data is not None:
                    ctx.source_map[ptr] = computable_data

                if src_ptr in ctx.env.pointer_specified_info:
                    ctx.env.pointer_derivation_map[src_ptr].append(ptr)

    else:
        raise TypeError("unsupported type in derive_view")

    ctx.view_nodes[derived.get_name(ctx.env.schema)] = derived

    if preserve_shape and stype in ctx.env.view_shapes:
        ctx.env.view_shapes[derived] = ctx.env.view_shapes[stype]

    ctx.env.created_schema_objects.add(derived)

    return derived