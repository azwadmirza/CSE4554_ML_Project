    def __init__(self, loss=None, metrics=None, output_shape=None, **kwargs):
        super().__init__(**kwargs)
        self.output_shape = output_shape
        self.loss = tf.keras.losses.get(loss)
        if metrics is None:
            metrics = []
        self.metrics = [tf.keras.metrics.get(metric) for metric in metrics]