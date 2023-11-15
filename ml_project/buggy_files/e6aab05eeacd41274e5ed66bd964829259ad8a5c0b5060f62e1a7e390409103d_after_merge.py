    def on_mouse_press(self, pos_scene):
        # self.print_mouse_event(event, 'Mouse press')
        # pos_scene = event.pos[:3]

        # find closest point to mouse and select it
        self.selected_point, self.selected_index = self.select_point(pos_scene)

        # if no point was clicked add a new one
        if self.selected_point is None:
            print("adding point", len(self.pos))
            self._pos = np.append(self.pos, [pos_scene[:3]], axis=0)
            self.set_data(pos=self.pos)
            self.marker_colors = np.ones((len(self.pos), 4), dtype=np.float32)
            self.selected_point = self.pos[-1]
            self.selected_index = len(self.pos) - 1

        # update markers and highlights
        self.update_markers(self.selected_index)