    def _on_display_change(self):
        parent = self.node.parent
        self.node.transforms = ChainTransform()
        self.node.parent = None

        if self.layer.dims.ndisplay == 2:
            self.node = Compound([Markers(), Markers(), Line()])
        else:
            self.node = Compound([Markers(), Markers()])
        self.node.parent = parent
        self._reset_base()