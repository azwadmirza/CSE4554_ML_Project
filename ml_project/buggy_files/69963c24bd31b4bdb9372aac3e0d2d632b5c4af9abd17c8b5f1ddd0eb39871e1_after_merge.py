    def __transfer_data_to_device(self, batch, device, gpu_id=None):
        if device == 'tpu' and XLA_AVAILABLE:
            # base case: object can be directly moved using `to`
            if callable(getattr(batch, 'to', None)):
                return batch.to(xm.xla_device())

        if device == 'gpu':
            # base case: object can be directly moved using `cuda` or `to`
            if callable(getattr(batch, 'cuda', None)):
                return batch.cuda(gpu_id)

            if callable(getattr(batch, 'to', None)):
                return batch.to(torch.device('cuda', gpu_id))

        # when list
        if isinstance(batch, list):
            for i, x in enumerate(batch):
                batch[i] = self.__transfer_data_to_device(x, device, gpu_id)
            return batch

        # when tuple
        if isinstance(batch, tuple):
            # when namedtuple
            if hasattr(batch, '_fields'):
                elem_type = type(batch)
                return elem_type(*(self.__transfer_data_to_device(x, device, gpu_id) for x in batch))
            else:
                batch = list(batch)
                for i, x in enumerate(batch):
                    batch[i] = self.__transfer_data_to_device(x, device, gpu_id)
                return tuple(batch)

        # when dict
        if isinstance(batch, dict):
            for k, v in batch.items():
                batch[k] = self.__transfer_data_to_device(v, device, gpu_id)

            return batch

        # nothing matches, return the value as is without transform
        return batch