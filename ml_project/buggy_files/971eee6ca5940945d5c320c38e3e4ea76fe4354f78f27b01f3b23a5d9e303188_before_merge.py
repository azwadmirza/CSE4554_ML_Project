    def start(self, endpoint, pool, distributed=True, schedulers=None, process_start_index=0):
        if schedulers:
            if isinstance(schedulers, six.string_types):
                schedulers = [schedulers]
            service_discover_addr = None
        else:
            schedulers = None
            service_discover_addr = options.kv_store

        if distributed:
            # create ClusterInfoActor
            self._cluster_info_ref = pool.create_actor(
                ClusterInfoActor, schedulers=schedulers, service_discover_addr=service_discover_addr,
                uid=ClusterInfoActor.default_name())

            # create process daemon
            from .daemon import WorkerDaemonActor
            actor_holder = self._daemon_ref = pool.create_actor(
                WorkerDaemonActor, uid=WorkerDaemonActor.default_name())

            # create StatusActor
            port_str = endpoint.rsplit(':', 1)[-1]
            self._status_ref = pool.create_actor(
                StatusActor, self._advertise_addr + ':' + port_str, uid=StatusActor.default_name())
        else:
            # create StatusActor
            self._status_ref = pool.create_actor(
                StatusActor, endpoint, uid=StatusActor.default_name())

            actor_holder = pool

        if self._ignore_avail_mem:
            # start a QuotaActor instead of MemQuotaActor to avoid memory size detection
            # for debug purpose only, DON'T USE IN PRODUCTION
            self._mem_quota_ref = pool.create_actor(
                QuotaActor, self._soft_mem_limit, uid=MemQuotaActor.default_name())
        else:
            self._mem_quota_ref = pool.create_actor(
                MemQuotaActor, self._soft_quota_limit, self._hard_mem_limit, uid=MemQuotaActor.default_name())

        # create ChunkHolderActor
        self._chunk_holder_ref = pool.create_actor(
            ChunkHolderActor, self._cache_mem_limit, uid=ChunkHolderActor.default_name())
        # create TaskQueueActor
        self._task_queue_ref = pool.create_actor(TaskQueueActor, uid=TaskQueueActor.default_name())
        # create DispatchActor
        self._dispatch_ref = pool.create_actor(DispatchActor, uid=DispatchActor.default_name())
        # create ExecutionActor
        self._execution_ref = pool.create_actor(ExecutionActor, uid=ExecutionActor.default_name())

        # create CpuCalcActor
        if not distributed:
            self._n_cpu_process = pool.cluster_info.n_process - 1 - process_start_index

        for cpu_id in range(self._n_cpu_process):
            uid = 'w:%d:mars-calc-%d-%d' % (cpu_id + 1, os.getpid(), cpu_id)
            actor = actor_holder.create_actor(CpuCalcActor, uid=uid)
            self._cpu_calc_actors.append(actor)

        if distributed:
            # create SenderActor and ReceiverActor
            start_pid = 1 + process_start_index + self._n_cpu_process
            for sender_id in range(self._n_io_process):
                uid = 'w:%d:mars-sender-%d-%d' % (start_pid + sender_id, os.getpid(), sender_id)
                actor = actor_holder.create_actor(SenderActor, uid=uid)
                self._sender_actors.append(actor)
            for receiver_id in range(2 * self._n_io_process):
                uid = 'w:%d:mars-receiver-%d-%d' % (start_pid + receiver_id // 2, os.getpid(), receiver_id)
                actor = actor_holder.create_actor(ReceiverActor, uid=uid)
                self._receiver_actors.append(actor)

        # create ProcessHelperActor
        for proc_id in range(pool.cluster_info.n_process - process_start_index):
            uid = 'w:%d:mars-process-helper-%d-%d' % (proc_id, os.getpid(), proc_id)
            actor = actor_holder.create_actor(ProcessHelperActor, uid=uid)
            self._process_helper_actors.append(actor)

        # create ResultSenderActor
        self._result_sender_ref = pool.create_actor(ResultSenderActor, uid=ResultSenderActor.default_name())

        # create SpillActor
        start_pid = pool.cluster_info.n_process - 1
        if options.worker.spill_directory:
            for spill_id in range(len(options.worker.spill_directory) * 2):
                uid = 'w:%d:mars-spill-%d-%d' % (start_pid, os.getpid(), spill_id)
                actor = actor_holder.create_actor(SpillActor, uid=uid)
                self._spill_actors.append(actor)