    def evaluate(self):
        val_iter = self.get_iterator('main')
        loss = 0
        count = 0
        self.model.eval()
        with torch.no_grad():
            for batch in copy.copy(val_iter):
                x, t = concat_examples(batch, device=self.device, padding=(0, -100))
                loss, count = self.model(x, t)
        self.model.train()
        # report validation loss
        observation = {}
        with reporter.report_scope(observation):
            reporter.report({'loss': float(loss.sum() / count.sum())}, self.model.reporter)
        return observation