    def start(self, endpoint, pool, distributed=True, discoverer=None, process_start_index=0):
        # create plasma key mapper
        from .storage import PlasmaKeyMapActor
        pool.create_actor(PlasmaKeyMapActor, uid=PlasmaKeyMapActor.default_uid())

        # create vineyard key mapper
        if options.vineyard.socket:  # pragma: no cover
            from .storage import VineyardKeyMapActor
            pool.create_actor(VineyardKeyMapActor, uid=VineyardKeyMapActor.default_uid())

        # create WorkerClusterInfoActor
        self._cluster_info_ref = pool.create_actor(
            WorkerClusterInfoActor, discoverer, distributed=distributed,
            uid=WorkerClusterInfoActor.default_uid())

        if distributed:
            # create process daemon
            from .daemon import WorkerDaemonActor
            actor_holder = self._daemon_ref = pool.create_actor(
                WorkerDaemonActor, uid=WorkerDaemonActor.default_uid())

            # create StatusActor
            if ':' not in self._advertise_addr:
                self._advertise_addr += ':' + endpoint.rsplit(':', 1)[-1]

            self._status_ref = pool.create_actor(
                StatusActor, self._advertise_addr, uid=StatusActor.default_uid())
        else:
            # create StatusActor
            self._status_ref = pool.create_actor(
                StatusActor, endpoint, with_gpu=self._n_cuda_process > 0, uid=StatusActor.default_uid())

            actor_holder = pool

        if self._ignore_avail_mem:
            # start a QuotaActor instead of MemQuotaActor to avoid memory size detection
            # for debug purpose only, DON'T USE IN PRODUCTION
            self._mem_quota_ref = pool.create_actor(
                QuotaActor, self._soft_mem_limit, uid=MemQuotaActor.default_uid())
        else:
            self._mem_quota_ref = pool.create_actor(
                MemQuotaActor, self._soft_quota_limit, self._hard_mem_limit, uid=MemQuotaActor.default_uid())

        # create StorageManagerActor
        self._storage_manager_ref = pool.create_actor(
            StorageManagerActor, uid=StorageManagerActor.default_uid())
        # create SharedHolderActor
        self._shared_holder_ref = pool.create_actor(
            SharedHolderActor, self._cache_mem_limit, uid=SharedHolderActor.default_uid())
        # create DispatchActor
        self._dispatch_ref = pool.create_actor(DispatchActor, uid=DispatchActor.default_uid())
        # create EventsActor
        self._events_ref = pool.create_actor(EventsActor, uid=EventsActor.default_uid())
        # create ReceiverNotifierActor
        self._receiver_manager_ref = pool.create_actor(ReceiverManagerActor, uid=ReceiverManagerActor.default_uid())
        # create ExecutionActor
        self._execution_ref = pool.create_actor(ExecutionActor, uid=ExecutionActor.default_uid())

        # create CpuCalcActor and InProcHolderActor
        if not distributed:
            self._n_cpu_process = pool.cluster_info.n_process - 1 - process_start_index

        for cpu_id in range(self._n_cpu_process):
            uid = 'w:%d:mars-cpu-calc-%d-%d' % (cpu_id + 1, os.getpid(), cpu_id)
            actor = actor_holder.create_actor(CpuCalcActor, uid=uid)
            self._cpu_calc_actors.append(actor)

            uid = 'w:%d:mars-inproc-holder-%d-%d' % (cpu_id + 1, os.getpid(), cpu_id)
            actor = actor_holder.create_actor(InProcHolderActor, uid=uid)
            self._inproc_holder_actors.append(actor)

            actor = actor_holder.create_actor(
                IORunnerActor, dispatched=False, uid=IORunnerActor.gen_uid(cpu_id + 1))
            self._inproc_io_runner_actors.append(actor)

        start_pid = 1 + self._n_cpu_process

        stats = resource.cuda_card_stats() if self._n_cuda_process else []
        for cuda_id, stat in enumerate(stats):
            for thread_no in range(options.worker.cuda_thread_num):
                uid = 'w:%d:mars-cuda-calc-%d-%d-%d' % (start_pid + cuda_id, os.getpid(), cuda_id, thread_no)
                actor = actor_holder.create_actor(CudaCalcActor, uid=uid)
                self._cuda_calc_actors.append(actor)

            uid = 'w:%d:mars-cuda-holder-%d-%d' % (start_pid + cuda_id, os.getpid(), cuda_id)
            actor = actor_holder.create_actor(
                CudaHolderActor, stat.fb_mem_info.total, device_id=stat.index, uid=uid)
            self._cuda_holder_actors.append(actor)

            actor = actor_holder.create_actor(
                IORunnerActor, dispatched=False, uid=IORunnerActor.gen_uid(start_pid + cuda_id))
            self._inproc_io_runner_actors.append(actor)

        start_pid += self._n_cuda_process

        if distributed:
            # create SenderActor and ReceiverActor
            for sender_id in range(self._n_net_process):
                uid = 'w:%d:mars-sender-%d-%d' % (start_pid + sender_id, os.getpid(), sender_id)
                actor = actor_holder.create_actor(SenderActor, uid=uid)
                self._sender_actors.append(actor)

        # Mutable requires ReceiverActor (with ClusterSession)
        for receiver_id in range(2 * self._n_net_process):
            uid = 'w:%d:mars-receiver-%d-%d' % (start_pid + receiver_id // 2, os.getpid(), receiver_id)
            actor = actor_holder.create_actor(ReceiverWorkerActor, uid=uid)
            self._receiver_actors.append(actor)

        # create ProcessHelperActor
        for proc_id in range(pool.cluster_info.n_process - process_start_index):
            uid = 'w:%d:mars-process-helper' % proc_id
            actor = actor_holder.create_actor(ProcessHelperActor, uid=uid)
            self._process_helper_actors.append(actor)

        # create ResultSenderActor
        self._result_sender_ref = pool.create_actor(ResultSenderActor, uid=ResultSenderActor.default_uid())

        # create SpillActor
        start_pid = pool.cluster_info.n_process - 1
        if options.worker.spill_directory:
            for spill_id in range(len(options.worker.spill_directory)):
                uid = 'w:%d:mars-global-io-runner-%d-%d' % (start_pid, os.getpid(), spill_id)
                actor = actor_holder.create_actor(IORunnerActor, uid=uid)
                self._spill_actors.append(actor)

        # worker can be registered when everything is ready
        self._status_ref.enable_status_upload(_tell=True)