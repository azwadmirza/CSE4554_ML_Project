    def _map_merge(dest: "BaseContainer", src: "BaseContainer") -> None:
        """merge src into dest and return a new copy, does not modified input"""
        from omegaconf import DictConfig, OmegaConf, ValueNode

        assert isinstance(dest, DictConfig)
        assert isinstance(src, DictConfig)
        src_type = src._metadata.object_type

        # if source DictConfig is an interpolation set the DictConfig one to be the same interpolation.
        if src._is_interpolation():
            dest._set_value(src._value())
            return
        # if source DictConfig is missing set the DictConfig one to be missing too.
        if src._is_missing():
            dest._set_value("???")
            return
        dest._validate_merge(key=None, value=src)

        def expand(node: Container) -> None:
            type_ = get_ref_type(node)
            if type_ is not None:
                _is_optional, type_ = _resolve_optional(type_)
                if is_dict_annotation(type_):
                    node._set_value({})
                elif is_list_annotation(type_):
                    node._set_value([])
                else:
                    node._set_value(type_)

        if dest._is_interpolation() or dest._is_missing():
            expand(dest)

        for key, src_value in src.items_ex(resolve=False):

            dest_node = dest._get_node(key, validate_access=False)
            if isinstance(dest_node, Container) and OmegaConf.is_none(dest, key):
                if not OmegaConf.is_none(src_value):
                    expand(dest_node)

            if dest_node is not None:
                if dest_node._is_interpolation():
                    target_node = dest_node._dereference_node(
                        throw_on_resolution_failure=False
                    )
                    if isinstance(target_node, Container):
                        dest[key] = target_node
                        dest_node = dest._get_node(key)

            if is_structured_config(dest._metadata.element_type):
                dest[key] = DictConfig(content=dest._metadata.element_type, parent=dest)
                dest_node = dest._get_node(key)

            if dest_node is not None:
                if isinstance(dest_node, BaseContainer):
                    if isinstance(src_value, BaseContainer):
                        dest._validate_merge(key=key, value=src_value)
                        dest_node._merge_with(src_value)
                    else:
                        dest.__setitem__(key, src_value)
                else:
                    if isinstance(src_value, BaseContainer):
                        dest.__setitem__(key, src_value)
                    else:
                        assert isinstance(dest_node, ValueNode)
                        try:
                            dest_node._set_value(src_value)
                        except (ValidationError, ReadonlyConfigError) as e:
                            dest._format_and_raise(key=key, value=src_value, cause=e)
            else:
                from omegaconf import open_dict

                if is_structured_config(src_type):
                    # verified to be compatible above in _validate_set_merge_impl
                    with open_dict(dest):
                        dest[key] = src._get_node(key)
                else:
                    dest[key] = src._get_node(key)

        if src_type is not None and not is_primitive_dict(src_type):
            dest._metadata.object_type = src_type

        # explicit flags on the source config are replacing the flag values in the destination
        flags = src._metadata.flags
        assert flags is not None
        for flag, value in flags.items():
            if value is not None:
                dest._set_flag(flag, value)