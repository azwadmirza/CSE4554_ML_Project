    def construct_rt_sequence(self, node, seqtyp, deep=False):
        # type: (Any, Any, bool) -> Any
        if not isinstance(node, SequenceNode):
            raise ConstructorError(
                None, None, 'expected a sequence node, but found %s' % node.id, node.start_mark
            )
        ret_val = []
        if node.comment:
            seqtyp._yaml_add_comment(node.comment[:2])
            if len(node.comment) > 2:
                seqtyp.yaml_end_comment_extend(node.comment[2], clear=True)
        if node.anchor:
            from dynaconf.vendor.ruamel.yaml.serializer import templated_id

            if not templated_id(node.anchor):
                seqtyp.yaml_set_anchor(node.anchor)
        for idx, child in enumerate(node.value):
            if child.comment:
                seqtyp._yaml_add_comment(child.comment, key=idx)
                child.comment = None  # if moved to sequence remove from child
            ret_val.append(self.construct_object(child, deep=deep))
            seqtyp._yaml_set_idx_line_col(
                idx, [child.start_mark.line, child.start_mark.column]
            )
        return ret_val