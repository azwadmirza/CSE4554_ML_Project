    def construct_mapping(self, node, deep=False):
        # Most of this is from yaml.constructor.SafeConstructor.  We replicate
        # it here so that we can warn users when they have duplicate dict keys
        # (pyyaml silently allows overwriting keys)
        if not isinstance(node, MappingNode):
            raise ConstructorError(None, None,
                                   "expected a mapping node, but found %s" % node.id,
                                   node.start_mark)
        self.flatten_mapping(node)
        mapping = AnsibleMapping()

        # Add our extra information to the returned value
        mapping.ansible_pos = self._node_position_info(node)

        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError as exc:
                raise ConstructorError("while constructing a mapping", node.start_mark,
                                       "found unacceptable key (%s)" % exc, key_node.start_mark)

            if key in mapping:
                msg = (u'While constructing a mapping from {1}, line {2}, column {3}, found a duplicate dict key ({0}).'
                       u' Using last defined value only.'.format(key, *mapping.ansible_pos))
                if C.DUPLICATE_YAML_DICT_KEY == 'warn':
                    display.warning(msg)
                elif C.DUPLICATE_YAML_DICT_KEY == 'error':
                    raise ConstructorError(to_native(msg))
                else:
                    # when 'ignore'
                    display.debug(msg)

            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value

        return mapping