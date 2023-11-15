    def _check_consider_get(self, node):
        def type_and_name_are_equal(node_a, node_b):
            for _type in [astroid.Name, astroid.AssignName]:
                if all(isinstance(_node, _type) for _node in [node_a, node_b]):
                    return node_a.name == node_b.name
            if all(isinstance(_node, astroid.Const) for _node in [node_a, node_b]):
                return node_a.value == node_b.value
            return False

        if_block_ok = (
            isinstance(node.test, astroid.Compare)
            and len(node.body) == 1
            and isinstance(node.body[0], astroid.Assign)
            and isinstance(node.body[0].value, astroid.Subscript)
            and type_and_name_are_equal(node.body[0].value.value, node.test.ops[0][1])
            and isinstance(node.body[0].value.slice, astroid.Index)
            and type_and_name_are_equal(node.body[0].value.slice.value, node.test.left)
            and len(node.body[0].targets) == 1
            and isinstance(node.body[0].targets[0], astroid.AssignName)
            and isinstance(utils.safe_infer(node.test.ops[0][1]), astroid.Dict))

        if if_block_ok and not node.orelse:
            self.add_message('consider-using-get', node=node)
        elif (if_block_ok and len(node.orelse) == 1
              and isinstance(node.orelse[0], astroid.Assign)
              and type_and_name_are_equal(node.orelse[0].targets[0], node.body[0].targets[0])
              and len(node.orelse[0].targets) == 1):
            self.add_message('consider-using-get', node=node)