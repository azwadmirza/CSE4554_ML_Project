    def on_mouse_move(self, event):
        # left mouse button
        if event.button == 1:
            # self.print_mouse_event(event, 'Mouse drag')
            if self.selected_point is not None:
                pos_scene = event.pos
                # update selected point to new position given by mouse
                self.selected_point[0] = round(pos_scene[0] / self.gridsize) \
                    * self.gridsize
                self.selected_point[1] = round(pos_scene[1] / self.gridsize) \
                    * self.gridsize
                self.set_data(pos=self.pos)
                self.update_markers(self.selected_index)

        else:
            #  if no button is pressed, just highlight the marker that would be
            # selected on click
            hl_point, hl_index = self.select_point(event)
            self.update_markers(hl_index, highlight_color=(0.5, 0.5, 1.0, 1.0))
            self.update()