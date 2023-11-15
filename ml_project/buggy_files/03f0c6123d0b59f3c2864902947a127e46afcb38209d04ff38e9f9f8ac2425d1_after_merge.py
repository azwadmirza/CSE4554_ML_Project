    def visit_try_without_finally(self, s: TryStmt, try_frame: bool) -> None:
        """Type check a try statement, ignoring the finally block.

        On entry, the top frame should receive all flow that exits the
        try block abnormally (i.e., such that the else block does not
        execute), and its parent should receive all flow that exits
        the try block normally.
        """
        # This frame will run the else block if the try fell through.
        # In that case, control flow continues to the parent of what
        # was the top frame on entry.
        with self.binder.frame_context(can_skip=False, fall_through=2, try_frame=try_frame):
            # This frame receives exit via exception, and runs exception handlers
            with self.binder.frame_context(can_skip=False, fall_through=2):
                # Finally, the body of the try statement
                with self.binder.frame_context(can_skip=False, fall_through=2, try_frame=True):
                    self.accept(s.body)
                for i in range(len(s.handlers)):
                    with self.binder.frame_context(can_skip=True, fall_through=4):
                        if s.types[i]:
                            t = self.visit_except_handler_test(s.types[i])
                            if s.vars[i]:
                                # To support local variables, we make this a definition line,
                                # causing assignment to set the variable's type.
                                s.vars[i].is_def = True
                                self.check_assignment(s.vars[i], self.temp_node(t, s.vars[i]))
                        self.accept(s.handlers[i])
                        if s.vars[i]:
                            # Exception variables are deleted in python 3 but not python 2.
                            # But, since it's bad form in python 2 and the type checking
                            # wouldn't work very well, we delete it anyway.

                            # Unfortunately, this doesn't let us detect usage before the
                            # try/except block.
                            if self.options.python_version[0] >= 3:
                                source = s.vars[i].name
                            else:
                                source = ('(exception variable "{}", which we do not '
                                          'accept outside except: blocks even in '
                                          'python 2)'.format(s.vars[i].name))
                            var = cast(Var, s.vars[i].node)
                            var.type = DeletedType(source=source)
                            self.binder.cleanse(s.vars[i])
            if s.else_body:
                self.accept(s.else_body)