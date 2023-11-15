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
                'display_id': self.display_id,
                'display_tail': self.display_tail,
                'display_graph': self.display_graph,
                'color_by': self.color_by,
                'colormap': self.colormap,
                'tail_width': self.tail_width,
                'tail_length': self.tail_length,
            }
        )
        return state