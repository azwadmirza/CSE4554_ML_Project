    def allow_jump(self, index: int) -> None:
        # self.frames and self.options_on_return have different lengths
        # so make sure the index is positive
        if index < 0:
            index += len(self.options_on_return)
        frame = Frame()
        for f in self.frames[index + 1:]:
            frame.update(f)
        self.options_on_return[index].append(frame)