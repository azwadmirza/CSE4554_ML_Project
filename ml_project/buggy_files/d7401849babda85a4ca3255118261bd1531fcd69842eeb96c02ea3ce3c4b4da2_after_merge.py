    def pop_frame(self, can_skip: bool, fall_through: int) -> Frame:
        """Pop a frame and return it.

        See frame_context() for documentation of fall_through.
        """

        if fall_through > 0:
            self.allow_jump(-fall_through)

        result = self.frames.pop()
        options = self.options_on_return.pop()

        if can_skip:
            options.insert(0, self.frames[-1])

        self.last_pop_changed = self.update_from_options(options)

        return result