    def visit_try_without_finally(self, s: TryStmt) -> bool:
        """Type check a try statement, ignoring the finally block.

        Return whether we are guaranteed to be breaking out.
        Otherwise, it will place the results possible frames of
        that don't break out into self.binder.frames[-2].
        """
        breaking_out = True
        # This frame records the possible states that exceptions can leave variables in
        # during the try: block
        with self.binder.frame_context():
            with self.binder.frame_context(3):
                self.binder.try_frames.add(len(self.binder.frames) - 2)
                self.accept(s.body)
                self.binder.try_frames.remove(len(self.binder.frames) - 2)
                if s.else_body:
                    self.accept(s.else_body)
            breaking_out = breaking_out and self.binder.last_pop_breaking_out
            for i in range(len(s.handlers)):
                with self.binder.frame_context(3):
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
                            source = ('(exception variable "{}", which we do not accept outside'
                                      'except: blocks even in python 2)'.format(s.vars[i].name))
                        var = cast(Var, s.vars[i].node)
                        var.type = DeletedType(source=source)
                        self.binder.cleanse(s.vars[i])
                breaking_out = breaking_out and self.binder.last_pop_breaking_out
        return breaking_out