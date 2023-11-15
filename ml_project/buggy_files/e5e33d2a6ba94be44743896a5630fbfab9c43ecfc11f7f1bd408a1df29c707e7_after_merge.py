    def _handle_simple_method_dict_pop(self, node, function, args, is_unbound_method):
        """Replace dict.pop() by a call to _PyDict_Pop().
        """
        if len(args) == 2:
            args.append(ExprNodes.NullNode(node.pos))
        elif len(args) != 3:
            self._error_wrong_arg_count('dict.pop', node, args, "2 or 3")
            return node

        return self._substitute_method_call(
            node, function,
            "__Pyx_PyDict_Pop", self.PyDict_Pop_func_type,
            'pop', is_unbound_method, args,
            may_return_none=True,
            utility_code=load_c_utility('py_dict_pop'))