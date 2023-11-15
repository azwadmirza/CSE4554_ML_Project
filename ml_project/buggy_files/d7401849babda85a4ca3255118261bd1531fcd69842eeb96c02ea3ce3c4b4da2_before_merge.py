    def pop_frame(self, fall_through: int = 0) -> Frame:
        """Pop a frame and return it.

        See frame_context() for documentation of fall_through.
        """
        if fall_through and not self.breaking_out:
            self.allow_jump(-fall_through)

        result = self.frames.pop()
        options = self.options_on_return.pop()

        self.last_pop_changed = self.update_from_options(options)
        self.last_pop_breaking_out = self.breaking_out

        return result