    def auto_add_sampler(self, dataloader: DataLoader, train: bool) -> DataLoader:

        # don't do anything if it's not a dataloader
        is_dataloader = isinstance(dataloader, DataLoader)
        # don't manipulate iterable datasets
        is_iterable_ds = _has_iterable_dataset(dataloader)

        if not is_dataloader or is_iterable_ds:
            return dataloader
        need_dist_sampler = (self.use_ddp or self.use_ddp2 or self.use_horovod or self.use_tpu)

        if self.replace_sampler_ddp and need_dist_sampler:
            if not isinstance(dataloader.sampler, (SequentialSampler, RandomSampler)):
                raise MisconfigurationException(
                    'You seem to have configured a sampler in your DataLoader. This will be replaced '
                    ' by `DistributedSampler` since `replace_sampler_ddp` is True and you are using'
                    ' distributed training. Either remove the sampler from your DataLoader or set'
                    ' `replace_sampler_ddp`=False if you want to use your custom sampler.')

            # replace with distributed sampler
            sampler = self._get_distributed_sampler(dataloader)
            dataloader = self.replace_sampler(dataloader, sampler)

        return dataloader