        def __check__(layers):
            if not isinstance(layers, collections.Sequence):
                __check_layer_type__(layers)
                layers = [layers]
            for layer in layers:
                __check_layer_type__(layer)
            return layers