    def __init__(self, layer: tf.keras.layers.Layer):
        self._layer = layer

        weights = layer.weights
        if isinstance(layer, tf.keras.layers.BatchNormalization):
            fused_pairs = [("beta", "moving_mean"), ("gamma", "moving_variance")]
            for pair in fused_pairs:
                names = [w.name.split("/")[-1].replace(":0", "") for w in weights]
                if pair[0] in names and pair[1] in names:
                    weights.pop(names.index(pair[0]))

        self.weight_profiles = [
            WeightProfile(
                weight, trainable=any(weight is w for w in layer.trainable_weights),
            )
            for weight in weights
        ]

        self.op_profiles = []

        if isinstance(layer, mac_containing_layers) and self.output_pixels:
            for p in self.weight_profiles:
                if not p.is_bias():
                    self.op_profiles.append(
                        OperationProfile(
                            n=p.count * self.output_pixels,
                            precision=max(self.input_precision or 32, p.bitwidth),
                            op_type="mac",
                        )
                    )