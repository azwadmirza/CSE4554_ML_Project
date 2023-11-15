    def _get_state(self):
        """Get dictionary of layer state.

        Returns
        -------
        state : dict
            Dictionary of layer state.
        """
        state = self._get_base_state()
        state.update(
            {
                'data': self.data,
                'properties': self.properties,
                'graph': self.graph,
                'color_by': self.color_by,
                'colormap': self.colormap,
                'colormaps_dict': self.colormaps_dict,
                'tail_width': self.tail_width,
                'tail_length': self.tail_length,
            }
        )
        return state