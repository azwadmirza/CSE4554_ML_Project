    def _calc_results(self, session_id, graph_key, graph, context_dict, chunk_targets):
        _, op_name = concat_operand_keys(graph, '_')

        logger.debug('Start calculating operand %s in %s.', graph_key, self.uid)
        start_time = time.time()

        for chunk in graph:
            for inp, prepare_inp, is_dep in zip(chunk.inputs, chunk.op.prepare_inputs, chunk.op.pure_depends):
                if not prepare_inp or is_dep:
                    context_dict[inp.key] = None

        local_context_dict = DistributedDictContext(
            self.get_scheduler(self.default_uid()), session_id, actor_ctx=self.ctx,
            address=self.address, n_cpu=self._get_n_cpu(), is_distributed=True,
            resource_ref=self._resource_ref)
        local_context_dict['_actor_cls'] = type(self)
        local_context_dict['_actor_uid'] = self.uid
        local_context_dict['_op_key'] = graph_key
        local_context_dict.update(context_dict)
        context_dict.clear()

        if self._execution_ref:
            self._execution_ref.deallocate_scheduler_resource(
                session_id, graph_key, delay=0.5, _tell=True, _wait=False)

        # start actual execution
        executor = Executor(storage=local_context_dict)
        with EventContext(self._events_ref, EventCategory.PROCEDURE, EventLevel.NORMAL,
                          self._calc_event_type, self.uid):
            self._execution_pool.submit(executor.execute_graph, graph,
                                        chunk_targets, retval=False).result()

        end_time = time.time()

        # collect results
        result_keys = []
        result_values, result_sizes, result_shapes = [], [], []
        collected_chunk_keys = set()
        for k in list(local_context_dict.keys()):
            v = local_context_dict[k]
            if isinstance(k, tuple):
                k = tuple(to_str(i) for i in k)
            else:
                k = to_str(k)

            chunk_key = get_chunk_key(k)
            if chunk_key in chunk_targets:
                result_keys.append(k)
                if self._calc_intermediate_device in self._calc_dest_devices:
                    result_values.append(v)
                    result_sizes.append(calc_data_size(v))
                else:
                    result_values.append(dataserializer.serialize(v))
                    result_sizes.append(result_values[-1].total_bytes)
                result_shapes.append(getattr(v, 'shape', None))
                collected_chunk_keys.add(chunk_key)

            local_context_dict.pop(k)

        # check if all targets generated
        if any(k not in collected_chunk_keys for k in chunk_targets):
            raise KeyError([k for k in chunk_targets if k not in collected_chunk_keys])

        # adjust sizes in allocation
        apply_allocs = defaultdict(lambda: 0)
        for k, size in zip(result_keys, result_sizes):
            apply_allocs[get_chunk_key(k)] += size

        apply_alloc_quota_keys, apply_alloc_sizes = [], []
        for k, v in apply_allocs.items():
            apply_alloc_quota_keys.append(build_quota_key(session_id, k, owner=self.proc_id))
            apply_alloc_sizes.append(v)
        self._mem_quota_ref.alter_allocations(apply_alloc_quota_keys, apply_alloc_sizes, _tell=True, _wait=False)
        self._mem_quota_ref.hold_quotas(apply_alloc_quota_keys, _tell=True)

        if self._status_ref:
            self._status_ref.update_mean_stats(
                'calc_speed.' + op_name, sum(apply_alloc_sizes) * 1.0 / (end_time - start_time),
                _tell=True, _wait=False)

        return self.storage_client.put_objects(
            session_id, result_keys, result_values, [self._calc_intermediate_device],
            sizes=result_sizes, shapes=result_shapes) \
            .then(lambda *_: result_keys)