    def update_core(self):
        # When we pass one iterator and optimizer to StandardUpdater.__init__,
        # they are automatically named 'main'.
        train_iter = self.get_iterator('main')
        optimizer = self.get_optimizer('main')
        # Progress the dataset iterator for sentences at each iteration.
        batch = train_iter.__next__()
        x, t = concat_examples(batch, device=self.device, padding=(0, -100))
        # Concatenate the token IDs to matrices and send them to the device
        # self.converter does this job
        # (it is chainer.dataset.concat_examples by default)
        loss = 0
        count = 0
        state = None
        batch_size, sequence_length = x.shape
        for i in six.moves.range(sequence_length):
            # Compute the loss at this time step and accumulate it
            state, loss_batch = self.model(state, x[:, i], t[:, i])
            non_zeros = torch.sum(x[:, i] != 0, dtype=torch.float)
            loss += loss_batch * non_zeros
            count += int(non_zeros)

        loss = loss.mean()
        reporter.report({'loss': float(loss.detach())}, optimizer.target)
        reporter.report({'count': count}, optimizer.target)
        # update
        self.model.zero_grad()  # Clear the parameter gradients
        loss.backward()  # Backprop
        if self.gradclip is not None:
            nn.utils.clip_grad_norm_(self.model.parameters(), self.gradclip)
        optimizer.step()  # Update the parameters