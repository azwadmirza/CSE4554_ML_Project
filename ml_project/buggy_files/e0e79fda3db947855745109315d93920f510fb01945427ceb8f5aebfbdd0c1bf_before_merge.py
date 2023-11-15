    def add_y_axis_label(self, frac):
        amt = self.visibleBox.ymin + frac*self.visibleBox.h
        srccol = self.ycols[0]
        txt = srccol.format(srccol.type(amt))

        # plot y-axis labels on the far left of the canvas, but within the plotview height-wise
        attr = colors.color_graph_axis
        self.plotlabel(0, self.plotviewBox.ymin + (1.0-frac)*self.plotviewBox.h, txt, attr)