    def _setup_engine(self):

        try:
            self._dataloader_len = len(self.state.dataloader) if hasattr(self.state.dataloader, "__len__") else None
        except TypeError:
            # _InfiniteConstantSampler can raise a TypeError on DataLoader length of a IterableDataset
            self._dataloader_len = None

        # setup seed here, as iter(data) can start prefetching
        self.setup_seed()

        # if input data is torch dataloader we replace batch sampler by a batch sampler
        # such that its random sampling indices are reproducible by prefetching them before data iteration
        if isinstance(self.state.dataloader, torch.utils.data.DataLoader):

            if (self._dataloader_len is not None) and hasattr(self.state.dataloader.sampler, "epoch"):
                if self._dataloader_len != self.state.epoch_length:
                    warnings.warn("When defined engine's epoch length is different of input dataloader length, "
                                  "distributed sampler indices can not be setup in a reproducible manner")

            batch_sampler = self.state.dataloader.batch_sampler
            if not isinstance(batch_sampler, ReproducibleBatchSampler):
                self.state.dataloader = _update_dataloader(self.state.dataloader,
                                                           ReproducibleBatchSampler(batch_sampler))

        iteration = self.state.iteration
        self._dataloader_iter = self._from_iteration(self.state.dataloader, iteration, self.state.epoch_length)

        # Below we define initial counter value for _run_once_on_dataset to measure a single epoch
        if self.state.epoch_length is not None:
            iteration %= self.state.epoch_length
        self._init_iter.append(iteration)