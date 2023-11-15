    def _on_graph_change(self, event=None):
        """ update the shader when the graph data changes """

        self.graph_shader.use_fade = self.layer.use_fade
        self.graph_shader.tail_length = self.layer.tail_length
        self.graph_shader.vertex_time = self.layer.graph_times

        # if the user clears a graph after it has been created, vispy offers
        # no method to clear the data, therefore, we need to set private
        # attributes to None to prevent errors
        if self.layer._view_graph is None:
            self.node._subvisuals[2]._pos = None
            self.node._subvisuals[2]._connect = None
            self.node.update()
            return

        self.node._subvisuals[2].set_data(
            pos=self.layer._view_graph,
            connect=self.layer.graph_connex,
            width=self.layer.tail_width,
            color='white',
        )

        # Call to update order of translation values with new dims:
        self._on_matrix_change()