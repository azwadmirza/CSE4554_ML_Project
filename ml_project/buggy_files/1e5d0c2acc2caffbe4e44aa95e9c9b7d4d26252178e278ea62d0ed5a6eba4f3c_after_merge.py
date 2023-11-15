    def __eq__(self, other):
        if not isinstance(other, CFGraph):
            raise NotImplementedError

        # A few derived items are checked to makes sure process() has been
        # invoked equally.
        for x in ['_nodes', '_edge_data', '_entry_point', '_preds', '_succs',
                  '_doms', '_back_edges']:
            this = getattr(self, x, None)
            that = getattr(other, x, None)
            if this != that:
                return False
        return True