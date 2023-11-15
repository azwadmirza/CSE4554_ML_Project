    def forward(self, x, t):
        """Reduce framewise loss values

        Args:
            x (torch.Tensor): Input ids. (batch, len)
            t (torch.Tensor): Target ids. (batch, len)

        Returns:
            tuple[torch.Tensor, torch.Tensor]: Tuple of
                the reduced loss value along time (scalar)
                and the number of valid loss values (scalar)
        """
        loss = 0
        count = torch.tensor(0).long()
        state = None
        batch_size, sequence_length = x.shape
        for i in six.moves.range(sequence_length):
            # Compute the loss at this time step and accumulate it
            state, loss_batch = self.model(state, x[:, i], t[:, i])
            non_zeros = torch.sum(x[:, i] != 0, dtype=torch.float)
            loss += loss_batch * non_zeros
            count += int(non_zeros)
        return loss, count.to(loss.device)