    def on_mouse_move(self, pos_scene):
        if self.selected_point is not None:
            # update selected point to new position given by mouse
            self.selected_point[0] = round(pos_scene[0] / self.gridsize) \
                * self.gridsize
            self.selected_point[1] = round(pos_scene[1] / self.gridsize) \
                * self.gridsize
            self.set_data(pos=self.pos)
            self.update_markers(self.selected_index)