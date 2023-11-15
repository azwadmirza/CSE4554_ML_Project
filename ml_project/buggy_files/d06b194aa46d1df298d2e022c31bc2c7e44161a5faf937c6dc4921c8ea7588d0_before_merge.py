    def frame_context(self, fall_through: int = 0) -> Iterator[Frame]:
        """Return a context manager that pushes/pops frames on enter/exit.

        If fall_through > 0, then it will allow the frame to escape to
        its ancestor `fall_through` levels higher.

        A simple 'with binder.frame_context(): pass' will change the
        last_pop_* flags but nothing else.
        """
        was_breaking_out = self.breaking_out
        yield self.push_frame()
        self.pop_frame(fall_through)
        self.breaking_out = was_breaking_out