    def auto_add_sampler(self, dataloader: DataLoader, train: bool) -> DataLoader:

        # don't do anything if it's not a dataloader
        if not isinstance(dataloader, DataLoader):
            return dataloader
        need_dist_sampler = (self.use_ddp or self.use_ddp2 or self.use_tpu)
        if self.replace_sampler_ddp and need_dist_sampler:

            skip_keys = ['sampler', 'batch_sampler', 'dataset_kind']

            dl_args = {
                k: v for k, v in dataloader.__dict__.items() if not k.startswith('_') and k not in skip_keys
            }

            if self.use_tpu:
                sampler = DistributedSampler(
                    dataloader.dataset,
                    num_replicas=xm.xrt_world_size(),
                    rank=xm.get_ordinal()
                )
            else:
                sampler = DistributedSampler(dataloader.dataset)

            dl_args['sampler'] = sampler
            dataloader = type(dataloader)(**dl_args)

        return dataloader