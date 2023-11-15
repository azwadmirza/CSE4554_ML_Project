    def get_config(self):
        config = super().get_config()
        config.update({
            'loss': self.loss,
            'metrics': self.metrics,
            'output_shape': self.output_shape
        })
        return config