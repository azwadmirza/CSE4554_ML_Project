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