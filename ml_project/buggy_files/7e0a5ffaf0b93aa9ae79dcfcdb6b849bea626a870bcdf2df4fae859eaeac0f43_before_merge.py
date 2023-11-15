    def __init__(self,
                 num_classes: Optional[int] = None,
                 multi_label: bool = False,
                 loss: Optional[types.LossType] = None,
                 metrics: Optional[types.MetricsType] = None,
                 dropout_rate: Optional[float] = None,
                 **kwargs):
        super().__init__(loss=loss,
                         metrics=metrics,
                         **kwargs)
        self.num_classes = num_classes
        self.multi_label = multi_label
        if not self.metrics:
            self.metrics = ['accuracy']
        self.dropout_rate = dropout_rate
        self.set_loss()