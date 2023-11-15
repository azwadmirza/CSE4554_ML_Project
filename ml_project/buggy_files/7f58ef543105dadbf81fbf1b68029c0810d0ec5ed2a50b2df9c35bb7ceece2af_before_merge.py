    def __init__(self, layers, extra_layers=None):
        def __check__(layers):
            if not isinstance(layers, collections.Sequence):
                __check_layer_type__(layers)
                layers = [layers]
            for layer in layers:
                __check_layer_type__(layer)
            return layers

        layers = __check__(layers)
        self.layers = layers
        if extra_layers is not None:
            extra_layers = __check__(extra_layers)

        self.__model_config__ = v2_layer.parse_network(
            layers, extra_layers=extra_layers)

        if extra_layers is not None:
            self.layers.extend(extra_layers)

        assert isinstance(self.__model_config__, ModelConfig)