    def __call__(self, value):
        """
        # Parameters

        value : `float`
            The value to average.
        """
        _total_value = list(self.detach_tensors(value))[0]
        _count = 1
        if is_distributed():
            device = torch.device("cpu")
            count = torch.tensor(_count).to(device)
            total_value = torch.tensor(_total_value).to(device)
            dist.all_reduce(count, op=dist.ReduceOp.SUM)
            dist.all_reduce(total_value, op=dist.ReduceOp.SUM)
            _count = count.item()
            _total_value = total_value.item()
        self._count += _count
        self._total_value += _total_value