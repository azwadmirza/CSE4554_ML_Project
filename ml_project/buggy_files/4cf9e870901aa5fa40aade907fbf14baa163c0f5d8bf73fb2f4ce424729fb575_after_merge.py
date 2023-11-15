    def scale_factor(self):
        """float: Conversion factor from canvas pixels to data coordinates.
        """
        if self.node.canvas is not None:
            transform = self.node.canvas.scene.node_transform(self.node)
            return transform.map([1, 1])[0] - transform.map([0, 0])[0]
        else:
            return 1