    def add_x_axis_label(self, frac):
        txt = self.formatX(self.visibleBox.xmin + frac*self.visibleBox.w)

        # plot x-axis labels below the plotviewBox.ymax, but within the plotview width-wise
        attr = colors.color_graph_axis
        xmin = self.plotviewBox.xmin + frac*self.plotviewBox.w
        if frac == 1.0:
            # shift rightmost label to be readable
            xmin -= max(len(txt)*2 - self.rightMarginPixels+1, 0)

        self.plotlabel(xmin, self.plotviewBox.ymax+4, txt, attr)