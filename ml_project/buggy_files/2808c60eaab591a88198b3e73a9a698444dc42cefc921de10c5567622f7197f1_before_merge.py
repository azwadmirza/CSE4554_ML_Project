    def get_config(self):
        blocks = [serialize(block) for block in self.blocks]
        nodes = {str(self._node_to_id[node]): serialize(node)
                 for node in self.inputs}
        override_hps = [tf.keras.utils.serialize_keras_object(hp)
                        for hp in self.override_hps]
        block_inputs = {
            str(block_id): [self._node_to_id[node]
                            for node in block.inputs]
            for block_id, block in enumerate(self.blocks)}
        block_outputs = {
            str(block_id): [self._node_to_id[node]
                            for node in block.outputs]
            for block_id, block in enumerate(self.blocks)}

        outputs = [self._node_to_id[node] for node in self.outputs]

        return {
            'override_hps': override_hps,  # List [serialized].
            'blocks': blocks,  # Dict {id: serialized}.
            'nodes': nodes,  # Dict {id: serialized}.
            'outputs': outputs,  # List of node_ids.
            'block_inputs': block_inputs,  # Dict {id: List of node_ids}.
            'block_outputs': block_outputs,  # Dict {id: List of node_ids}.
        }