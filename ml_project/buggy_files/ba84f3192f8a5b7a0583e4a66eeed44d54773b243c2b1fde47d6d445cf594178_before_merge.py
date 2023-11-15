    def construct_mapping(self, node, maptyp, deep=False):  # type: ignore
        # type: (Any, Any, bool) -> Any
        if not isinstance(node, MappingNode):
            raise ConstructorError(
                None, None, 'expected a mapping node, but found %s' % node.id, node.start_mark
            )
        merge_map = self.flatten_mapping(node)
        # mapping = {}
        if node.comment:
            maptyp._yaml_add_comment(node.comment[:2])
            if len(node.comment) > 2:
                maptyp.yaml_end_comment_extend(node.comment[2], clear=True)
        if node.anchor:
            from ruamel.yaml.serializer import templated_id

            if not templated_id(node.anchor):
                maptyp.yaml_set_anchor(node.anchor)
        last_key, last_value = None, self._sentinel
        for key_node, value_node in node.value:
            # keys can be list -> deep
            key = self.construct_object(key_node, deep=True)
            # lists are not hashable, but tuples are
            if not isinstance(key, Hashable):
                if isinstance(key, MutableSequence):
                    key_s = CommentedKeySeq(key)
                    if key_node.flow_style is True:
                        key_s.fa.set_flow_style()
                    elif key_node.flow_style is False:
                        key_s.fa.set_block_style()
                    key = key_s
                elif isinstance(key, MutableMapping):
                    key_m = CommentedKeyMap(key)
                    if key_node.flow_style is True:
                        key_m.fa.set_flow_style()
                    elif key_node.flow_style is False:
                        key_m.fa.set_block_style()
                    key = key_m
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
            value = self.construct_object(value_node, deep=deep)
            if self.check_mapping_key(node, key_node, maptyp, key, value):
                if key_node.comment and len(key_node.comment) > 4 and key_node.comment[4]:
                    if last_value is None:
                        key_node.comment[0] = key_node.comment.pop(4)
                        maptyp._yaml_add_comment(key_node.comment, value=last_key)
                    else:
                        key_node.comment[2] = key_node.comment.pop(4)
                        maptyp._yaml_add_comment(key_node.comment, key=key)
                    key_node.comment = None
                if key_node.comment:
                    maptyp._yaml_add_comment(key_node.comment, key=key)
                if value_node.comment:
                    maptyp._yaml_add_comment(value_node.comment, value=key)
                maptyp._yaml_set_kv_line_col(
                    key,
                    [
                        key_node.start_mark.line,
                        key_node.start_mark.column,
                        value_node.start_mark.line,
                        value_node.start_mark.column,
                    ],
                )
                maptyp[key] = value
                last_key, last_value = key, value  # could use indexing
        # do this last, or <<: before a key will prevent insertion in instances
        # of collections.OrderedDict (as they have no __contains__
        if merge_map:
            maptyp.add_yaml_merge(merge_map)