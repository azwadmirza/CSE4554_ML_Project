    def construct_setting(self, node, typ, deep=False):
        # type: (Any, Any, bool) -> Any
        if not isinstance(node, MappingNode):
            raise ConstructorError(
                None, None, 'expected a mapping node, but found %s' % node.id, node.start_mark
            )
        if node.comment:
            typ._yaml_add_comment(node.comment[:2])
            if len(node.comment) > 2:
                typ.yaml_end_comment_extend(node.comment[2], clear=True)
        if node.anchor:
            from dynaconf.vendor.ruamel.yaml.serializer import templated_id

            if not templated_id(node.anchor):
                typ.yaml_set_anchor(node.anchor)
        for key_node, value_node in node.value:
            # keys can be list -> deep
            key = self.construct_object(key_node, deep=True)
            # lists are not hashable, but tuples are
            if not isinstance(key, Hashable):
                if isinstance(key, list):
                    key = tuple(key)
            if PY2:
                try:
                    hash(key)
                except TypeError as exc:
                    raise ConstructorError(
                        'while constructing a mapping',
                        node.start_mark,
                        'found unacceptable key (%s)' % exc,
                        key_node.start_mark,
                    )
            else:
                if not isinstance(key, Hashable):
                    raise ConstructorError(
                        'while constructing a mapping',
                        node.start_mark,
                        'found unhashable key',
                        key_node.start_mark,
                    )
            # construct but should be null
            value = self.construct_object(value_node, deep=deep)  # NOQA
            self.check_set_key(node, key_node, typ, key)
            if key_node.comment:
                typ._yaml_add_comment(key_node.comment, key=key)
            if value_node.comment:
                typ._yaml_add_comment(value_node.comment, value=key)
            typ.add(key)