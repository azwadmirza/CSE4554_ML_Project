    def _remove_layer(self, event):
        """When a layer is removed, remove its parent.

        Parameters
        ----------
        event : qtpy.QtCore.QEvent
            Event from the Qt context.
        """
        layer = event.item
        vispy_layer = self.layer_to_visual[layer]
        vispy_layer.node.transforms = ChainTransform()
        vispy_layer.node.parent = None
        del self.layer_to_visual[layer]