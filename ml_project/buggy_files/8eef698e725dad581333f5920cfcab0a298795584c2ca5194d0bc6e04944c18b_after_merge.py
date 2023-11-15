    def _from_iteration(data, iteration):
        if isinstance(data, torch.utils.data.DataLoader):
            try:
                # following is unsafe for IterableDatasets
                iteration %= len(data.batch_sampler)
                if iteration > 0:
                    # batch sampler is ReproducibleBatchSampler
                    data.batch_sampler.start_iteration = iteration
            except TypeError:
                # Probably we can do nothing with DataLoader built upon IterableDatasets
                pass
            data_iter = iter(data)
        else:
            if hasattr(data, "__len__"):
                iteration %= len(data)
            data_iter = iter(data)
            counter = 0
            while counter < iteration:
                try:
                    next(data_iter)
                    counter += 1
                except StopIteration:
                    data_iter = iter(data)

        return data_iter