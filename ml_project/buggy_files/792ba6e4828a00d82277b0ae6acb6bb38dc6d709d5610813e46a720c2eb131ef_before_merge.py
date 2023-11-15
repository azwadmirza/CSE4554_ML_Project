    def _allocate_resource(self, session_id, op_key, op_info, target_worker=None, reject_workers=None):
        """
        Allocate resource for single operand
        :param session_id: session id
        :param op_key: operand key
        :param op_info: operand info dict
        :param target_worker: worker to allocate, can be None
        :param reject_workers: workers denied to assign to
        """
        if target_worker not in self._worker_metrics:
            target_worker = None

        reject_workers = reject_workers or set()

        op_io_meta = op_info.get('io_meta', {})
        try:
            input_metas = op_io_meta['input_data_metas']
        except KeyError:
            input_metas = self._get_chunks_meta(session_id, op_io_meta.get('input_chunks', {}))
            missing_keys = [k for k, m in input_metas.items() if m is None]
            if missing_keys:
                raise DependencyMissing(f'Dependencies {missing_keys!r} missing for operand {op_key}')

        if target_worker is None:
            input_sizes = dict((k, v.chunk_size) for k, v in input_metas.items())
            who_has = dict((k, meta.workers) for k, meta in input_metas.items())
            candidate_workers = self._get_eps_by_worker_locality(who_has, input_sizes)
        else:
            candidate_workers = [target_worker]

        candidate_workers = [w for w in candidate_workers if w not in reject_workers]
        if not candidate_workers:
            return None, []

        # todo make more detailed allocation plans
        calc_device = op_info.get('calc_device', 'cpu')

        try:
            mem_usage = self._mem_usage_cache[op_key]
        except KeyError:
            mem_usage = self._mem_usage_cache[op_key] = sum(v.chunk_size for v in input_metas.values())

        if calc_device == 'cpu':
            alloc_dict = dict(cpu=options.scheduler.default_cpu_usage, mem_quota=mem_usage)
        elif calc_device == 'cuda':
            alloc_dict = dict(cuda=options.scheduler.default_cuda_usage, mem_quota=mem_usage)
        else:  # pragma: no cover
            raise NotImplementedError(f'Calc device {calc_device} not supported')

        last_assign = self._session_last_assigns.get(session_id, time.time())
        timeout_on_fail = time.time() - last_assign > options.scheduler.assign_timeout

        rejects = []
        for worker_ep in candidate_workers:
            if self._resource_ref.allocate_resource(
                    session_id, op_key, worker_ep, alloc_dict, log_fail=timeout_on_fail):
                logger.debug('Operand %s(%s) allocated to run in %s', op_key, op_info['op_name'], worker_ep)
                self._mem_usage_cache.pop(op_key, None)

                self.get_actor_ref(BaseOperandActor.gen_uid(session_id, op_key)) \
                    .submit_to_worker(worker_ep, input_metas, _tell=True, _wait=False)
                return worker_ep, rejects
            else:
                rejects.append(worker_ep)

        if timeout_on_fail:
            running_ops = sum(len(metrics.get('progress', dict()).get(str(session_id), dict()))
                              for metrics in self._worker_metrics.values())
            if running_ops == 0:
                raise TimeoutError(f'Assign resources to operand {op_key} timed out')
            else:
                self._session_last_assigns[session_id] = time.time()
        return None, rejects