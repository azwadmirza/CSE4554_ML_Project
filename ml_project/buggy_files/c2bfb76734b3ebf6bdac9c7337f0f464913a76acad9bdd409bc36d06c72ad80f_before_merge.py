    def visit_try_stmt(self, s: TryStmt) -> Type:
        """Type check a try statement."""
        completed_frames = []  # type: List[Frame]
        self.binder.push_frame()
        self.binder.try_frames.add(len(self.binder.frames) - 2)
        self.accept(s.body)
        self.binder.try_frames.remove(len(self.binder.frames) - 2)
        if s.else_body:
            self.accept(s.else_body)
        self.breaking_out = False
        changed, frame_on_completion = self.binder.pop_frame()
        completed_frames.append(frame_on_completion)

        for i in range(len(s.handlers)):
            self.binder.push_frame()
            if s.types[i]:
                t = self.exception_type(s.types[i])
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
                if self.pyversion[0] >= 3:
                    source = s.vars[i].name
                else:
                    source = ('(exception variable "{}", which we do not accept '
                              'outside except: blocks even in python 2)'.format(s.vars[i].name))
                var = cast(Var, s.vars[i].node)
                var.type = DeletedType(source=source)
                self.binder.cleanse(s.vars[i])

            self.breaking_out = False
            changed, frame_on_completion = self.binder.pop_frame()
            completed_frames.append(frame_on_completion)

        self.binder.update_from_options(completed_frames)

        if s.finally_body:
            self.accept(s.finally_body)