    def _update_patch_size(self):
        if self.is_on() and self.patch:
            ro, ri = self.size
            self.patch[0].radius = ro
            if ri > 0:
                self.patch[1].radius = ri
            self._update_resizers()
            self.draw_patch()