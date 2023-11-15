    def get_config(self):
        config = super().get_config()
        config.update({
            'loss': tf.keras.losses.serialize(self.loss),
            'metrics': [tf.keras.metrics.serialize(metric)
                        for metric in self.metrics],
            'output_shape': self.output_shape
        })
        return config