    def __init__(self,
                 num_classes: Optional[int] = None,
                 multi_label: bool = False,
                 loss: Optional[types.LossType] = None,
                 metrics: Optional[types.MetricsType] = None,
                 dropout_rate: Optional[float] = None,
                 **kwargs):
        self.num_classes = num_classes
        self.multi_label = multi_label
        self.dropout_rate = dropout_rate
        if metrics is None:
            metrics = ['accuracy']
        if loss is None:
            loss = self.infer_loss()
        super().__init__(loss=loss,
                         metrics=metrics,
                         **kwargs)