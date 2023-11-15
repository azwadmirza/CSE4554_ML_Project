    def __init__(self, val_iter, eval_model, reporter, device):
        super(LMEvaluator, self).__init__(
            val_iter, reporter, device=device)
        self.model = eval_model