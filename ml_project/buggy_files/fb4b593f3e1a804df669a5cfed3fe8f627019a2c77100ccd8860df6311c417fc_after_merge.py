def ptrref_from_ptrcls(
    *,
    schema: s_schema.Schema,
    ptrcls: s_pointers.PointerLike,
    direction: s_pointers.PointerDirection = (
        s_pointers.PointerDirection.Outbound),
    cache: Optional[Dict[PtrRefCacheKey, irast.BasePointerRef]] = None,
    typeref_cache: Optional[Dict[TypeRefCacheKey, irast.TypeRef]] = None,
    include_descendants: bool = False,
) -> irast.BasePointerRef:
    """Return an IR pointer descriptor for a given schema pointer.

    An IR PointerRef is an object that fully describes a schema pointer for
    the purposes of query compilation.

    Args:
        schema:
            A schema instance, in which the type *t* is defined.
        ptrcls:
            A :class:`schema.pointers.Pointer` instance for which to
            return the PointerRef.
        direction:
            The direction of the pointer in the path expression.

    Returns:
        An instance of a subclass of :class:`ir.ast.BasePointerRef`
        corresponding to the given schema pointer.
    """

    if cache is not None:
        cached = cache.get((ptrcls, direction, include_descendants))
        if cached is not None:
            return cached

    kwargs: Dict[str, Any] = {}

    ircls: Type[irast.BasePointerRef]

    source_ref: Optional[irast.TypeRef]
    target_ref: Optional[irast.TypeRef]
    out_source: Optional[irast.TypeRef]

    if isinstance(ptrcls, irast.TupleIndirectionLink):
        ircls = irast.TupleIndirectionPointerRef
    elif isinstance(ptrcls, irast.TypeIntersectionLink):
        ircls = irast.TypeIntersectionPointerRef
        kwargs['optional'] = ptrcls.is_optional()
        kwargs['is_empty'] = ptrcls.is_empty()
        kwargs['is_subtype'] = ptrcls.is_subtype()
        kwargs['rptr_specialization'] = ptrcls.get_rptr_specialization()
    elif isinstance(ptrcls, s_pointers.Pointer):
        ircls = irast.PointerRef
        kwargs['id'] = ptrcls.id
        name = ptrcls.get_name(schema)
        kwargs['module_id'] = schema.get_global(
            s_mod.Module, name.module).id
    else:
        raise AssertionError(f'unexpected pointer class: {ptrcls}')

    target = ptrcls.get_far_endpoint(schema, direction)
    if target is not None and not isinstance(target, irast.TypeRef):
        assert isinstance(target, s_types.Type)
        target_ref = type_to_typeref(schema, target, cache=typeref_cache)
    else:
        target_ref = target

    source = ptrcls.get_near_endpoint(schema, direction)

    source_ptr: Optional[irast.BasePointerRef]
    if (isinstance(ptrcls, s_props.Property)
            and isinstance(source, s_links.Link)):
        source_ptr = ptrref_from_ptrcls(
            ptrcls=source,
            direction=direction,
            schema=schema,
            cache=cache,
            typeref_cache=typeref_cache,
        )
        source_ref = None
    else:
        if source is not None and not isinstance(source, irast.TypeRef):
            assert isinstance(source, s_types.Type)
            source_ref = type_to_typeref(schema,
                                         source,
                                         cache=typeref_cache)
        else:
            source_ref = source
        source_ptr = None

    if direction is s_pointers.PointerDirection.Inbound:
        out_source = target_ref
        out_target = source_ref
    else:
        out_source = source_ref
        out_target = target_ref

    out_cardinality, dir_cardinality = cardinality_from_ptrcls(
        schema, ptrcls, direction=direction)

    material_ptrcls = ptrcls.material_type(schema)
    material_ptr: Optional[irast.BasePointerRef]
    if material_ptrcls is not None and material_ptrcls is not ptrcls:
        material_ptr = ptrref_from_ptrcls(
            ptrcls=material_ptrcls,
            direction=direction,
            schema=schema,
            cache=cache,
            typeref_cache=typeref_cache,
            include_descendants=include_descendants,
        )
    else:
        material_ptr = None

    union_components: Set[irast.BasePointerRef] = set()
    union_of = ptrcls.get_union_of(schema)
    union_is_concrete = False
    if union_of:
        union_ptrs = set()

        for component in union_of.objects(schema):
            assert isinstance(component, s_pointers.Pointer)
            material_comp = component.material_type(schema)
            union_ptrs.add(material_comp)

        non_overlapping, union_is_concrete = s_utils.get_non_overlapping_union(
            schema,
            union_ptrs,
        )

        union_components = {
            ptrref_from_ptrcls(
                ptrcls=p,
                direction=direction,
                schema=schema,
                cache=cache,
                typeref_cache=typeref_cache,
            ) for p in non_overlapping
        }

    std_parent_name = None
    for ancestor in ptrcls.get_ancestors(schema).objects(schema):
        ancestor_name = ancestor.get_name(schema)
        if ancestor_name.module == 'std' and ancestor.generic(schema):
            std_parent_name = ancestor_name
            break

    is_derived = ptrcls.get_is_derived(schema)
    base_ptr: Optional[irast.BasePointerRef]
    if is_derived:
        base_ptrcls = ptrcls.get_bases(schema).first(schema)
        top_ptr_name = type(base_ptrcls).get_default_base_name()
        if base_ptrcls.get_name(schema) != top_ptr_name:
            base_ptr = ptrref_from_ptrcls(
                ptrcls=base_ptrcls,
                direction=direction,
                schema=schema,
                cache=cache,
                typeref_cache=typeref_cache,
            )
        else:
            base_ptr = None
    else:
        base_ptr = None

    if (
        material_ptr is None
        and include_descendants
        and isinstance(ptrcls, s_pointers.Pointer)
    ):
        descendants = frozenset(
            ptrref_from_ptrcls(
                ptrcls=child,
                direction=direction,
                schema=schema,
                cache=cache,
                typeref_cache=typeref_cache,
            )
            for child in ptrcls.children(schema)
            if not child.get_is_derived(schema)
        )
    else:
        descendants = frozenset()

    kwargs.update(dict(
        out_source=out_source,
        out_target=out_target,
        name=ptrcls.get_name(schema),
        shortname=ptrcls.get_shortname(schema),
        path_id_name=ptrcls.get_path_id_name(schema),
        std_parent_name=std_parent_name,
        direction=direction,
        source_ptr=source_ptr,
        base_ptr=base_ptr,
        material_ptr=material_ptr,
        descendants=descendants,
        is_derived=ptrcls.get_is_derived(schema),
        is_computable=ptrcls.get_computable(schema),
        union_components=union_components,
        union_is_concrete=union_is_concrete,
        has_properties=ptrcls.has_user_defined_properties(schema),
        dir_cardinality=dir_cardinality,
        out_cardinality=out_cardinality,
    ))

    ptrref = ircls(**kwargs)

    if cache is not None:
        cache[ptrcls, direction, include_descendants] = ptrref

    return ptrref