    def select(self):
        """
        Cause this widget to be the selected widget in its MPL axes. This
        assumes that the widget has its patch added to the MPL axes.
        """
        if not self.patch or not self.is_on() or not self.ax:
            return

        canvas = self.ax.figure.canvas
        # Simulate a pick event
        x, y = self.patch[0].get_transform().transform_point((0, 0))
        mouseevent = MouseEvent('pick_event', canvas, x, y)
        # when the widget is added programatically, mouseevent can be "empty"
        if mouseevent.button:
            canvas.pick_event(mouseevent, self.patch[0])
        self.picked = False