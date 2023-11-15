    def on_mouse_press_event(self, event):
        self.selected_node = dict()
        enclosing_nodes = self.scatter_nodes.contains(event)
        # Example value for enclosing nodes: (True, {'ind': array([ 71, 340], dtype=int32)})
        if enclosing_nodes[0]:
            index = enclosing_nodes[1]['ind'][-1]
            self.selected_node['public_key'] = self.node_positions.keys()[index]
            self.redraw = True