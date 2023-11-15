def _trace_op(
    op: sd.Command,
    opbranch: List[sd.Command],
    depgraph: DepGraph,
    renames: Dict[sn.Name, sn.Name],
    renames_r: Dict[sn.Name, sn.Name],
    strongrefs: Dict[sn.Name, sn.Name],
    old_schema: Optional[s_schema.Schema],
    new_schema: s_schema.Schema,
) -> None:
    def get_deps(key: DepGraphKey) -> DepGraphEntry:
        try:
            item = depgraph[key]
        except KeyError:
            item = depgraph[key] = DepGraphEntry(
                item=(),
                deps=ordered.OrderedSet(),
                weak_deps=ordered.OrderedSet(),
            )
        return item

    def record_field_deps(
        op: sd.AlterObjectProperty,
        parent_op: sd.ObjectCommand[so.Object],
    ) -> str:
        if isinstance(op.new_value, (so.Object, so.ObjectShell)):
            nvn = op.new_value.get_name(new_schema)
            if nvn is not None:
                deps.add(('create', str(nvn)))
                deps.add(('alter', str(nvn)))
                if nvn in renames_r:
                    deps.add(('rename', str(renames_r[nvn])))

        graph_key = f'{parent_op.classname}%%{op.property}'
        deps.add(('create', str(parent_op.classname)))

        if isinstance(op.old_value, (so.Object, so.ObjectShell)):
            assert old_schema is not None
            ovn = op.old_value.get_name(old_schema)
            nvn = op.new_value.get_name(new_schema)
            if ovn != nvn:
                ov_item = get_deps(('delete', str(ovn)))
                ov_item.deps.add((tag, graph_key))

        return graph_key

    def write_dep_matrix(
        dependent: str,
        dependent_tags: Tuple[str, ...],
        dependency: str,
        dependency_tags: Tuple[str, ...],
        *,
        as_weak: bool = False,
    ) -> None:
        for dependent_tag in dependent_tags:
            item = get_deps((dependent_tag, dependent))
            for dependency_tag in dependency_tags:
                if as_weak:
                    item.weak_deps.add((dependency_tag, dependency))
                else:
                    item.deps.add((dependency_tag, dependency))

    deps: ordered.OrderedSet[Tuple[str, str]] = ordered.OrderedSet()
    graph_key: str
    implicit_ancestors: List[sn.Name] = []

    if isinstance(op, sd.CreateObject):
        tag = 'create'
    elif isinstance(op, sd.AlterObject):
        tag = 'alter'
    elif isinstance(op, sd.RenameObject):
        tag = 'rename'
    elif isinstance(op, inheriting.RebaseInheritingObject):
        tag = 'rebase'
    elif isinstance(op, sd.DeleteObject):
        tag = 'delete'
    elif isinstance(op, referencing.AlterOwned):
        tag = 'alterowned'
    elif isinstance(op, (sd.AlterObjectProperty, sd.AlterSpecialObjectField)):
        tag = 'field'
    else:
        raise RuntimeError(
            f'unexpected delta command type at top level: {op!r}'
        )

    if isinstance(op, (sd.DeleteObject, referencing.AlterOwned)):
        assert old_schema is not None
        obj = get_object(old_schema, op)
        refs = _get_referrers(old_schema, obj, strongrefs)
        for ref in refs:
            ref_name_str = str(ref.get_name(old_schema))
            if (
                (
                    isinstance(obj, referencing.ReferencedObject)
                    and obj.get_referrer(old_schema) == ref
                )
            ):
                # If the referrer is enclosing the object
                # (i.e. the reference is a refdict reference),
                # we sort the referrer operation first.
                ref_item = get_deps(('delete', ref_name_str))
                ref_item.deps.add((tag, str(op.classname)))

            elif (
                isinstance(ref, referencing.ReferencedInheritingObject)
                and (
                    op.classname
                    in {
                        b.get_name(old_schema)
                        for b in ref.get_implicit_ancestors(old_schema)
                    }
                )
                and (
                    not isinstance(ref, s_pointers.Pointer)
                    or not ref.get_from_alias(old_schema)
                )
            ):
                # If the ref is an implicit descendant (i.e. an inherited ref),
                # we also sort it _after_ the parent, because we'll pull
                # it as a child of the parent op at the time of tree
                # reassembly.
                ref_item = get_deps(('delete', ref_name_str))
                ref_item.deps.add((tag, str(op.classname)))

            elif (
                isinstance(ref, referencing.ReferencedObject)
                and ref.get_referrer(old_schema) == obj
            ):
                # Skip refdict.backref_attr to avoid dependency cycles.
                continue

            else:
                # Otherwise, things must be deleted _after_ their referrers
                # have been deleted or altered.
                deps.add(('delete', ref_name_str))
                deps.add(('rebase', ref_name_str))

        if isinstance(obj, referencing.ReferencedObject):
            referrer = obj.get_referrer(old_schema)
            if referrer is not None:
                assert isinstance(referrer, so.QualifiedObject)
                referrer_name: sn.Name = referrer.get_name(old_schema)
                if referrer_name in renames_r:
                    referrer_name = renames_r[referrer_name]

                # For SET OWNED, we need any rebase of the enclosing
                # object to come *after*, because otherwise obj could
                # get dropped before the SET OWNED takes effect.
                # For DROP OWNED and DROP we want it after the rebase.
                is_set_owned = (
                    isinstance(op, referencing.AlterOwned)
                    and op.get_attribute_value('owned')
                )
                if is_set_owned:
                    ref_item = get_deps(('rebase', str(referrer_name)))
                    ref_item.deps.add(('alterowned', str(op.classname)))
                else:
                    deps.add(('rebase', str(referrer_name)))

                if (
                    isinstance(obj, referencing.ReferencedInheritingObject)
                    and (
                        not isinstance(obj, s_pointers.Pointer)
                        or not obj.get_from_alias(old_schema)
                    )
                ):
                    for ancestor in obj.get_implicit_ancestors(old_schema):
                        ancestor_name = ancestor.get_name(old_schema)
                        implicit_ancestors.append(ancestor_name)
                        anc_item = get_deps(('delete', str(ancestor_name)))
                        anc_item.deps.add(('alterowned', str(op.classname)))

                        if is_set_owned:
                            # SET OWNED must come before ancestor rebases too
                            anc_item = get_deps(('rebase', str(ancestor_name)))
                            anc_item.deps.add(
                                ('alterowned', str(op.classname)))

        graph_key = str(op.classname)

    elif isinstance(op, sd.AlterObjectProperty):
        parent_op = opbranch[-2]
        assert isinstance(parent_op, sd.ObjectCommand)
        graph_key = record_field_deps(op, parent_op)

    elif isinstance(op, sd.AlterSpecialObjectField):
        parent_op = opbranch[-2]
        assert isinstance(parent_op, sd.ObjectCommand)
        field_op = op._get_attribute_set_cmd(op._field)
        assert field_op is not None
        graph_key = record_field_deps(field_op, parent_op)

    elif isinstance(op, sd.ObjectCommand):
        # If the object was renamed, use the new name, else use regular.
        name = renames.get(op.classname, op.classname)
        obj = get_object(new_schema, op, name)
        this_name_str = str(op.classname)

        if tag == 'rename':
            # On renames, we want to delete any references before we
            # do the rename. This is because for functions and
            # constraints we implicitly rename the object when
            # something it references is renamed, and this implicit
            # rename can interfere with a CREATE/DELETE pair.  So we
            # make sure to put the DELETE before the RENAME of a
            # referenced object. (An improvement would be to elide a
            # CREATE/DELETE pair when it could be implicitly handled
            # by a rename).
            assert old_schema
            old_obj = get_object(old_schema, op, op.classname)
            for ref in _get_referrers(old_schema, old_obj, strongrefs):
                deps.add(('delete', str(ref.get_name(old_schema))))

        refs = _get_referrers(new_schema, obj, strongrefs)
        for ref in refs:
            ref_name = ref.get_name(new_schema)
            if ref_name in renames_r:
                ref_name = renames_r[ref_name]
            ref_name_str = str(ref_name)

            if ((isinstance(ref, referencing.ReferencedObject)
                    and ref.get_referrer(new_schema) == obj)
                    or (isinstance(obj, referencing.ReferencedObject)
                        and obj.get_referrer(new_schema) == ref)):
                # Mostly ignore refs generated by refdict backref, but
                # make create/alter depend on renames of the backref.
                # This makes sure that a rename is done before the innards are
                # modified. DDL doesn't actually require this but some of the
                # internals for producing the DDL do (since otherwise we can
                # generate references to the renamed type in our delta before
                # it is renamed).
                if tag in ('create', 'alter'):
                    deps.add(('rename', ref_name_str))

                continue

            write_dep_matrix(
                dependent=ref_name_str,
                dependent_tags=('create', 'alter', 'rebase'),
                dependency=this_name_str,
                dependency_tags=('create', 'alter', 'rename'),
            )

            item = get_deps(('rename', ref_name_str))
            item.deps.add(('create', this_name_str))
            item.deps.add(('alter', this_name_str))

            if isinstance(ref, s_pointers.Pointer):
                # The current item is a type referred to by
                # a link or property in another type.  Set the referring
                # type and its descendants as weak dependents of the current
                # item to reduce the number of unnecessary ALTERs in the
                # final delta, especially ones that might result in SET TYPE
                # commands being generated.
                ref_src = ref.get_source(new_schema)
                if isinstance(ref_src, s_pointers.Pointer):
                    ref_src_src = ref_src.get_source(new_schema)
                    if ref_src_src is not None:
                        ref_src = ref_src_src
                if ref_src is not None:
                    for desc in ref_src.descendants(new_schema) | {ref_src}:
                        desc_name = str(desc.get_name(new_schema))

                        write_dep_matrix(
                            dependent=desc_name,
                            dependent_tags=('create', 'alter'),
                            dependency=this_name_str,
                            dependency_tags=('create', 'alter', 'rename'),
                            as_weak=True,
                        )

        if tag in ('create', 'alter'):
            # In a delete/create cycle, deletion must obviously
            # happen first.
            deps.add(('delete', str(op.classname)))

            if isinstance(obj, s_func.Function) and old_schema is not None:
                old_funcs = old_schema.get_functions(
                    sn.shortname_from_fullname(op.classname),
                    default=(),
                )
                for old_func in old_funcs:
                    deps.add(('delete', str(old_func.get_name(old_schema))))

        if tag == 'alter':
            # Alteration must happen after creation, if any.
            deps.add(('create', this_name_str))
            deps.add(('rename', this_name_str))
            deps.add(('rebase', this_name_str))

        if isinstance(obj, referencing.ReferencedObject):
            referrer = obj.get_referrer(new_schema)
            if referrer is not None:
                assert isinstance(referrer, so.QualifiedObject)
                referrer_name = referrer.get_name(new_schema)
                if referrer_name in renames_r:
                    referrer_name = renames_r[referrer_name]
                ref_name_str = str(referrer_name)
                deps.add(('create', ref_name_str))
                deps.add(('rebase', ref_name_str))

                if isinstance(obj, referencing.ReferencedInheritingObject):
                    implicit_ancestors = [
                        b.get_name(new_schema)
                        for b in obj.get_implicit_ancestors(new_schema)
                    ]

                    if not isinstance(op, sd.CreateObject):
                        assert old_schema is not None
                        name = renames_r.get(op.classname, op.classname)
                        old_obj = get_object(old_schema, op, name)
                        assert isinstance(
                            old_obj,
                            referencing.ReferencedInheritingObject,
                        )
                        implicit_ancestors += [
                            b.get_name(old_schema)
                            for b in old_obj.get_implicit_ancestors(old_schema)
                        ]

        graph_key = this_name_str

    else:
        raise AssertionError(f'unexpected op type: {op!r}')

    item = get_deps((tag, graph_key))

    item.item = tuple(opbranch)
    item.deps |= deps
    item.extra = DepGraphEntryExtra(
        implicit_ancestors=[renames_r.get(a, a) for a in implicit_ancestors],
    )