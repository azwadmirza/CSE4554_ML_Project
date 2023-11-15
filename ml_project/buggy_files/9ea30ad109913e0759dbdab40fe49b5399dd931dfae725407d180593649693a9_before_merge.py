    def _dump_cache(self, session_id, graph_key, inproc_uid, save_sizes):
        """
        Dump calc results into shared cache or spill
        :param session_id: session id
        :param graph_key: key of the execution graph
        :param inproc_uid: uid of the InProcessCacheActor
        :param save_sizes: sizes of data
        """
        graph_record = self._graph_records[session_id, graph_key]
        chunk_keys = graph_record.chunk_targets
        calc_keys = list(save_sizes.keys())
        send_addresses = graph_record.send_addresses

        logger.debug('Graph %s: Start putting %r into shared cache. Target actor uid %s.',
                     graph_key, chunk_keys, inproc_uid)
        self._update_state(session_id, graph_key, ExecutionState.STORING)

        raw_inproc_ref = self.ctx.actor_ref(inproc_uid)
        inproc_ref = self.promise_ref(raw_inproc_ref)

        if graph_record.stop_requested:
            logger.debug('Graph %s already marked for stop, quit.', graph_key)
            if (self._daemon_ref is None or self._daemon_ref.is_actor_process_alive(raw_inproc_ref)) \
                    and self.ctx.has_actor(raw_inproc_ref):
                logger.debug('Try remove keys for graph %s.', graph_key)
                raw_inproc_ref.remove_cache(session_id, list(calc_keys), _tell=True)
            logger.debug('Graph %s already marked for stop, quit.', graph_key)
            raise ExecutionInterrupted

        self._chunk_holder_ref.unpin_chunks(
            graph_key, list(set(c.key for c in graph_record.graph)), _tell=True)
        self._dump_execution_states()

        if self._daemon_ref is not None and not self._daemon_ref.is_actor_process_alive(raw_inproc_ref):
            raise WorkerProcessStopped

        def _cache_result(*_):
            self._result_cache[(session_id, graph_key)] = GraphResultRecord(save_sizes)

        if not send_addresses:
            # no endpoints to send, dump keys into shared memory and return
            logger.debug('Worker graph %s(%s) finished execution. Dumping results into plasma...',
                         graph_key, graph_record.op_string)
            return inproc_ref.dump_cache(session_id, calc_keys, _promise=True) \
                .then(_cache_result)
        else:
            # dump keys into shared memory and send
            all_addresses = [{v} if isinstance(v, six.string_types) else set(v)
                             for v in send_addresses.values()]
            all_addresses = list(reduce(lambda a, b: a | b, all_addresses, set()))
            logger.debug('Worker graph %s(%s) finished execution. Dumping results into plasma '
                         'while actively transferring into %r...',
                         graph_key, graph_record.op_string, all_addresses)

            data_to_addresses = dict((k, v) for k, v in send_addresses.items()
                                     if k in save_sizes)

            return inproc_ref.dump_cache(session_id, calc_keys, _promise=True) \
                .then(save_sizes.update) \
                .then(lambda *_: functools.partial(self._do_active_transfer,
                                                   session_id, graph_key, data_to_addresses)) \
                .then(_cache_result)