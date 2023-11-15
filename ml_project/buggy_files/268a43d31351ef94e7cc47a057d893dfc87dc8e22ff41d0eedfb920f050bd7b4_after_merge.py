def _create_defaults_tree_impl(
    repo: IConfigRepository,
    root: DefaultsTreeNode,
    is_root_config: bool,
    skip_missing: bool,
    interpolated_subtree: bool,
    overrides: Overrides,
) -> DefaultsTreeNode:
    parent = root.node
    children: List[Union[InputDefault, DefaultsTreeNode]] = []
    if parent.is_virtual():
        if is_root_config:
            return _expand_virtual_root(repo, root, overrides, skip_missing)
        else:
            return root

    if is_root_config:
        root.node.update_parent("", "")
        if not repo.config_exists(root.node.get_config_path()):
            config_not_found_error(repo=repo, tree=root)

    update_package_header(repo=repo, node=parent)

    if overrides.is_deleted(parent):
        overrides.delete(parent)
        return root

    overrides.set_known_choice(parent)

    if parent.get_name() is None:
        return root

    if _check_not_missing(repo=repo, default=parent, skip_missing=skip_missing):
        return root

    path = parent.get_config_path()
    loaded = repo.load_config(config_path=path)

    if loaded is None:
        if parent.is_optional():
            assert isinstance(parent, (GroupDefault, ConfigDefault))
            parent.deleted = True
            return root
        config_not_found_error(repo=repo, tree=root)

    assert loaded is not None
    defaults_list = copy.deepcopy(loaded.defaults_list)
    if defaults_list is None:
        defaults_list = []

    self_added = False
    if (
        len(defaults_list) > 0
        or is_root_config
        and len(overrides.append_group_defaults) > 0
    ):
        self_added = _validate_self(containing_node=parent, defaults=defaults_list)

    if is_root_config:
        defaults_list.extend(overrides.append_group_defaults)

    _update_overrides(defaults_list, overrides, parent, interpolated_subtree)

    def add_child(
        child_list: List[Union[InputDefault, DefaultsTreeNode]],
        new_root_: DefaultsTreeNode,
    ) -> None:
        subtree_ = _create_defaults_tree_impl(
            repo=repo,
            root=new_root_,
            is_root_config=False,
            interpolated_subtree=interpolated_subtree,
            skip_missing=skip_missing,
            overrides=overrides,
        )
        if subtree_.children is None:
            child_list.append(new_root_.node)
        else:
            child_list.append(subtree_)

    for d in reversed(defaults_list):
        if d.is_self():
            d.update_parent(root.node.parent_base_dir, root.node.get_package())
            children.append(d)
        else:
            if d.is_override():
                continue

            d.update_parent(parent.get_group_path(), parent.get_final_package())

            if overrides.is_overridden(d):
                assert isinstance(d, GroupDefault)
                overrides.override_default_option(d)

            if isinstance(d, GroupDefault) and d.is_options():
                # overriding may change from options to name
                if d.is_options():
                    for item in reversed(d.get_options()):
                        if "${" in item:
                            raise ConfigCompositionException(
                                f"In '{path}': Defaults List interpolation is not supported in options list items"
                            )

                        assert d.group is not None
                        node = ConfigDefault(
                            path=d.group + "/" + item,
                            package=d.package,
                            optional=d.is_optional(),
                        )
                        node.update_parent(
                            parent.get_group_path(), parent.get_final_package()
                        )
                        new_root = DefaultsTreeNode(node=node, parent=root)
                        add_child(children, new_root)
                else:
                    new_root = DefaultsTreeNode(node=d, parent=root)
                    add_child(children, new_root)

            else:
                if d.is_interpolation():
                    children.append(d)
                    continue

                new_root = DefaultsTreeNode(node=d, parent=root)
                add_child(children, new_root)

    # processed deferred interpolations
    known_choices = _create_interpolation_map(overrides, defaults_list, self_added)

    for idx, dd in enumerate(children):
        if isinstance(dd, InputDefault) and dd.is_interpolation():
            if not parent.primary:
                # Interpolations from nested configs would require much more work
                # If you have a compelling use case please file an feature request.
                path = parent.get_config_path()
                raise ConfigCompositionException(
                    f"In '{path}': Defaults List interpolation is only supported in the primary config"
                )
            dd.resolve_interpolation(known_choices)
            new_root = DefaultsTreeNode(node=dd, parent=root)
            dd.update_parent(parent.get_group_path(), parent.get_final_package())
            subtree = _create_defaults_tree_impl(
                repo=repo,
                root=new_root,
                is_root_config=False,
                skip_missing=skip_missing,
                interpolated_subtree=True,
                overrides=overrides,
            )
            if subtree.children is not None:
                children[idx] = subtree

    if len(children) > 0:
        root.children = list(reversed(children))

    return root