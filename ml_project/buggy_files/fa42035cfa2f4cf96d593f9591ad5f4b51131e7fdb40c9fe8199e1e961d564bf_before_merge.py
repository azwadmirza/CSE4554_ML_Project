    def _check_stop_iteration_inside_generator(self, node):
        """Check if an exception of type StopIteration is raised inside a generator"""
        frame = node.frame()
        if not isinstance(frame, astroid.FunctionDef) or not frame.is_generator():
            return
        if utils.node_ignores_exception(node, StopIteration):
            return
        if not node.exc:
            return
        exc = utils.safe_infer(node.exc)
        if exc is not None and self._check_exception_inherit_from_stopiteration(exc):
            self.add_message('stop-iteration-return', node=node)