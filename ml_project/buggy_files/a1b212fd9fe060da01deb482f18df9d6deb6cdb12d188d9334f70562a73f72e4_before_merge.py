    def from_config(cls, config):
        blocks = [deserialize(block) for block in config['blocks']]
        nodes = {int(node_id): deserialize(node)
                 for node_id, node in config['nodes'].items()}
        override_hps = [kerastuner.engine.hyperparameters.deserialize(config)
                        for config in config['override_hps']]

        inputs = [nodes[node_id] for node_id in nodes]
        for block_id, block in enumerate(blocks):
            input_nodes = [nodes[node_id]
                           for node_id in config['block_inputs'][str(block_id)]]
            output_nodes = nest.flatten(block(input_nodes))
            for output_node, node_id in zip(
                    output_nodes, config['block_outputs'][str(block_id)]):
                nodes[node_id] = output_node

        outputs = [nodes[node_id] for node_id in config['outputs']]
        return cls(inputs=inputs, outputs=outputs, override_hps=override_hps)