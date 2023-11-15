    def create_pool(self, *args, **kwargs):
        self._service = SchedulerService(disable_failover=self.args.disable_failover)
        self.n_process = int(self.args.nproc or resource.cpu_count())
        kwargs['distributor'] = MarsDistributor(self.n_process, 's:h1:')
        return super().create_pool(*args, **kwargs)