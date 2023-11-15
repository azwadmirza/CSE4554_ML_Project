    def add_y_axis_label(self, frac):
        txt = self.formatY(self.visibleBox.ymin + frac*self.visibleBox.h)

        # plot y-axis labels on the far left of the canvas, but within the plotview height-wise
        attr = colors.color_graph_axis
        self.plotlabel(0, self.plotviewBox.ymin + (1.0-frac)*self.plotviewBox.h, txt, attr)