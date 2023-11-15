    def __init__(self,
                 output_dim: Optional[int] = None,
                 loss: types.LossType = 'mean_squared_error',
                 metrics: Optional[types.MetricsType] = None,
                 dropout_rate: Optional[float] = None,
                 **kwargs):
        super().__init__(loss=loss,
                         metrics=metrics,
                         **kwargs)
        self.output_dim = output_dim
        if not self.metrics:
            self.metrics = ['mean_squared_error']
        self.loss = loss
        self.dropout_rate = dropout_rate