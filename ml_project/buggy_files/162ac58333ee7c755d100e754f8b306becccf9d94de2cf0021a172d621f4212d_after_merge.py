    def _update_patch_size(self):
        if self.is_on() and self.patch:
            ro, ri = self.size
            self.patch[0].radius = ro
            if ri > 0:
                # Add the inner circle
                if len(self.patch) == 1:
                    # Need to remove the previous patch before using 
                    # `_add_patch_to`
                    self.ax.artists.remove(self.patch[0])
                    self.patch = []
                    self._add_patch_to(self.ax)
                self.patch[1].radius = ri
            self._update_resizers()
            self.draw_patch()