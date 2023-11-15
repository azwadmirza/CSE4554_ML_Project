    def _dense_block_end_node(self, layer_id):
        return self._block_end_node(layer_id, Constant.DENSE_BLOCK_DISTANCE)