    def draw(self, renderer):
        if not self.get_visible():
            return

        self._update(renderer)  # update the tick

        size = self._ticksize
        path_trans = self.get_transform()

        gc = renderer.new_gc()
        gc.set_foreground(self.get_markeredgecolor())
        gc.set_linewidth(self.get_markeredgewidth())
        gc.set_alpha(self._alpha)

        offset = renderer.points_to_pixels(size)
        marker_scale = Affine2D().scale(offset, offset)

        if self.get_tick_out():
            add_angle = 180
        else:
            add_angle = 0

        marker_rotation = Affine2D()
        marker_transform = marker_scale + marker_rotation

        for loc, angle in self.locs_angles:
            marker_rotation.clear().rotate_deg(angle+add_angle)
            locs = path_trans.transform_non_affine([loc])
            if self.axes and not self.axes.viewLim.contains(*locs[0]):
                continue
            renderer.draw_markers(gc, self._tickvert_path, marker_transform,
                                  Path(locs), path_trans.get_affine())

        gc.restore()