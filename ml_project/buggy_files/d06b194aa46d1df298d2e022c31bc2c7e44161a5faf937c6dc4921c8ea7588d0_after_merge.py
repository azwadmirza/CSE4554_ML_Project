    def frame_context(self, *, can_skip: bool, fall_through: int = 1,
                      break_frame: int = 0, continue_frame: int = 0,
                      try_frame: bool = False) -> Iterator[Frame]:
        """Return a context manager that pushes/pops frames on enter/exit.

        If can_skip is True, control flow is allowed to bypass the
        newly-created frame.

        If fall_through > 0, then it will allow control flow that
        falls off the end of the frame to escape to its ancestor
        `fall_through` levels higher. Otherwise control flow ends
        at the end of the frame.

        If break_frame > 0, then 'break' statements within this frame
        will jump out to the frame break_frame levels higher than the
        frame created by this call to frame_context. Similarly for
        continue_frame and 'continue' statements.

        If try_frame is true, then execution is allowed to jump at any
        point within the newly created frame (or its descendents) to
        its parent (i.e., to the frame that was on top before this
        call to frame_context).

        After the context manager exits, self.last_pop_changed indicates
        whether any types changed in the newly-topmost frame as a result
        of popping this frame.
        """
        assert len(self.frames) > 1

        if break_frame:
            self.break_frames.append(len(self.frames) - break_frame)
        if continue_frame:
            self.continue_frames.append(len(self.frames) - continue_frame)
        if try_frame:
            self.try_frames.add(len(self.frames) - 1)

        new_frame = self.push_frame()
        if try_frame:
            # An exception may occur immediately
            self.allow_jump(-1)
        yield new_frame
        self.pop_frame(can_skip, fall_through)

        if break_frame:
            self.break_frames.pop()
        if continue_frame:
            self.continue_frames.pop()
        if try_frame:
            self.try_frames.remove(len(self.frames) - 1)