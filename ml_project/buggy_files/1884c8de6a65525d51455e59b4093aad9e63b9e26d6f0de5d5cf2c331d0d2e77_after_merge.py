    def create_pool(self, *args, **kwargs):
        # here we create necessary actors on worker
        # and distribute them over processes

        cuda_devices = [self.args.cuda_device] if self.args.cuda_device else None
        self._service = WorkerService(
            advertise_addr=self.args.advertise,
            n_cpu_process=self.args.cpu_procs,
            n_net_process=self.args.net_procs or self.args.io_procs,
            cuda_devices=cuda_devices,
            spill_dirs=self.args.spill_dir,
            io_parallel_num=self.args.io_parallel_num,
            total_mem=self.args.phy_mem,
            cache_mem_limit=self.args.cache_mem,
            ignore_avail_mem=self.args.ignore_avail_mem,
            min_mem_size=self.args.min_mem,
            disk_compression=self.args.disk_compression.lower(),
            transfer_compression=self.args.transfer_compression.lower(),
            plasma_dir=self.args.plasma_dir,
            use_ext_plasma_dir=bool(self.args.plasma_dir),
            disable_proc_recover=self.args.disable_proc_recover,
        )
        # start plasma
        self._service.start_plasma()

        self.n_process = self._service.n_process
        kwargs['distributor'] = MarsDistributor(self.n_process, 'w:0:')
        return super().create_pool(*args, **kwargs)