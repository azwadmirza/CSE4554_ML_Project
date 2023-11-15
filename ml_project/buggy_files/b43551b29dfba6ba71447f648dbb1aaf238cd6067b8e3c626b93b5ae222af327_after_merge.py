    def update_core(self):
        # When we pass one iterator and optimizer to StandardUpdater.__init__,
        # they are automatically named 'main'.
        train_iter = self.get_iterator('main')
        optimizer = self.get_optimizer('main')
        # Progress the dataset iterator for sentences at each iteration.
        batch = train_iter.__next__()
        # Concatenate the token IDs to matrices and send them to the device
        # self.converter does this job
        # (it is chainer.dataset.concat_examples by default)
        x, t = concat_examples(batch, device=self.device, padding=(0, -100))
        loss, count = self.model(x, t)
        loss = loss.sum()
        count = count.sum()
        reporter.report({'loss': float(loss.detach() / count)}, optimizer.target)
        reporter.report({'count': int(count)}, optimizer.target)
        # update
        self.model.zero_grad()  # Clear the parameter gradients
        loss.backward()  # Backprop
        if self.gradclip is not None:
            nn.utils.clip_grad_norm_(self.model.parameters(), self.gradclip)
        optimizer.step()  # Update the parameters