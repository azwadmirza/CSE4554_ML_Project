    def evaluate(self):
        val_iter = self.get_iterator('main')
        loss = 0
        count = 0
        self.model.eval()
        with torch.no_grad():
            for batch in copy.copy(val_iter):
                x, t = concat_examples(batch, device=self.device, padding=(0, -100))
                state = None
                for i in six.moves.range(len(x[0])):
                    state, loss_batch = self.model(state, x[:, i], t[:, i])
                    non_zeros = torch.sum(x[:, i] != 0, dtype=torch.float)
                    loss += loss_batch * non_zeros
                    count += int(non_zeros)
        self.model.train()
        # report validation loss
        observation = {}
        with reporter.report_scope(observation):
            reporter.report({'loss': float(loss.mean() / count)}, self.model.reporter)
        return observation