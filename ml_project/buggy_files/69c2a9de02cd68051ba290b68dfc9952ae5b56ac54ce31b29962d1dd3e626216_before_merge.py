    def set_distributed_mode(self, distributed_backend: Optional[str] = None):

        if distributed_backend is not None:
            self.distributed_backend = distributed_backend

        if isinstance(self.distributed_backend, Accelerator):
            return

        if self.distributed_backend is None:
            if self.has_horovodrun():
                self._set_horovod_backend()
            elif self.num_gpus == 0 and (self.num_nodes > 1 or self.num_processes > 1):
                self._distrib_type = DistributedType.DDP
            elif self.num_gpus > 1:
                rank_zero_warn(
                    'You requested multiple GPUs but did not specify a backend, e.g.'
                    ' `Trainer(accelerator="dp"|"ddp"|"ddp2")`. Setting `accelerator="ddp_spawn"` for you.'
                )
                self.distributed_backend = "ddp_spawn"

        # special case with DDP on CPUs
        if self.distributed_backend == "ddp_cpu":
            self._distrib_type = DistributedType.DDP
            if self.num_gpus > 0:
                rank_zero_warn(
                    'You requested one or more GPUs, but set the backend to `ddp_cpu`. Training will not use GPUs.'
                )
                self.parallel_device_ids = None
            if self.num_processes is None:
                # define the max CPU available
                self.num_processes = os.cpu_count()
        # special case with TPUs
        elif self.distributed_backend == 'tpu':
            self._device_type = DeviceType.TPU
        elif self.distributed_backend and self._distrib_type is None:
            self._distrib_type = DistributedType(self.distributed_backend)

        # unless you request explicitly for CPU and some GPU are available use them
        _on_cpu = self.distributed_backend and 'cpu' in self.distributed_backend
        if self.num_gpus > 0 and not _on_cpu:
            self._device_type = DeviceType.GPU

        _distrib_types = (DistributedType.DP, DistributedType.DDP, DistributedType.DDP_SPAWN, DistributedType.DDP2)
        # DP and DDP2 cannot run without GPU
        if self.num_gpus == 0 and self._distrib_type in _distrib_types and not _on_cpu:
            rank_zero_warn(
                'You requested distributed training on GPUs, but none is available, so we set backend to `ddp_cpu`.'
            )
            # todo: in some cases it yield in comarison None and int
            if (self.num_nodes and self.num_nodes > 1) or (self.num_processes and self.num_processes > 1):
                self._distrib_type = DistributedType.DDP
            else:
                rank_zero_warn('You are running on single node with no parallelization, so distributed has no effect.')
                self._distrib_type = None

        # finished configuring self._distrib_type, check ipython environment
        self.check_interactive_compatibility()

        # for DDP overwrite nb processes by requested GPUs
        if (
            self._device_type == DeviceType.GPU
            and self._distrib_type in (DistributedType.DDP, DistributedType.DDP_SPAWN)
        ):
            self.num_processes = self.num_gpus

        if (self._device_type == DeviceType.GPU and self._distrib_type == DistributedType.DDP2):
            self.num_processes = self.num_nodes

        # Horovod is an extra case...
        if self.distributed_backend == "horovod":
            self._set_horovod_backend()

        using_valid_distributed = self.use_ddp or self.use_ddp2
        if self.num_nodes > 1 and not using_valid_distributed:
            # throw error to force user to choose a supported distributed type such as ddp or ddp2
            raise MisconfigurationException(
                'Your chosen distributed type does not support num_nodes > 1. '
                'Please set accelerator=ddp or accelerator=ddp2.'
            )

        rank_zero_info(f'GPU available: {torch.cuda.is_available()}, used: {self._device_type == DeviceType.GPU}')
        num_cores = self.tpu_cores if self.tpu_cores is not None else 0
        rank_zero_info(f'TPU available: {_TPU_AVAILABLE}, using: {num_cores} TPU cores')

        if torch.cuda.is_available() and self._device_type != DeviceType.GPU:
            rank_zero_warn(
                "GPU available but not used. Set the gpus flag in your trainer"
                " `Trainer(gpus=1)` or script `--gpus=1`."
            )