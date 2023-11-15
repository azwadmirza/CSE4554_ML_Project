    def __init__(self, y_true=None, y_pred=None, type_true=None, type_pred=None, **kw):
        super().__init__(_y_true=y_true, _y_pred=y_pred,
                         _type_true=type_true, _type_pred=type_pred, **kw)
        # scalar(y_type), y_true, y_pred
        self.output_types = [OutputType.tensor] * 3