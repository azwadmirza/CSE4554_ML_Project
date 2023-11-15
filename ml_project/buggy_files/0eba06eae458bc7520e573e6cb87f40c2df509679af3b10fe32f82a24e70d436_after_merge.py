    def handle_worker_change(self, adds, removes, lost_chunks, handle_later=True):
        """
        Calculate and propose changes of operand states given changes
        in workers and lost chunks.

        :param adds: endpoints of workers newly added to the cluster
        :param removes: endpoints of workers removed to the cluster
        :param lost_chunks: keys of lost chunks
        :param handle_later: run the function later, only used in this actor
        """
        if self._state in GraphState.TERMINATED_STATES:
            return

        if handle_later:
            # Run the fail-over process later.
            # This is the default behavior as we need to make sure that
            # all crucial state changes are received by GraphActor.
            # During the delay, no operands are allowed to be freed.
            self._operand_free_paused = True
            self._worker_adds.update(adds)
            self._worker_removes.update(removes)
            self.ref().handle_worker_change(adds, removes, lost_chunks,
                                            handle_later=False, _delay=0.5, _tell=True)
            return
        else:
            self._operand_free_paused = False

        adds = self._worker_adds
        self._worker_adds = set()
        removes = self._worker_removes
        self._worker_removes = set()
        if not adds and not removes:
            return

        if all(ep in self._assigned_workers for ep in adds) \
                and not any(ep in self._assigned_workers for ep in removes):
            return

        worker_slots = self._get_worker_slots()
        self._assigned_workers = set(worker_slots)
        removes_set = set(removes)

        # collect operand states
        operand_infos = self._operand_infos
        fixed_assigns = dict()
        graph_states = dict()
        for key, op_info in operand_infos.items():
            op_worker = op_info.get('worker')
            if op_worker is None:
                continue

            op_state = graph_states[key] = op_info['state']

            # RUNNING nodes on dead workers should be moved to READY first
            if op_state == OperandState.RUNNING and op_worker in removes_set:
                graph_states[key] = OperandState.READY

            if op_worker in worker_slots:
                fixed_assigns[key] = op_info['worker']

        graph = self.get_chunk_graph()
        new_states = dict()
        ordered_states = OrderedDict(
            sorted(((k, v) for k, v in graph_states.items()),
                   key=lambda d: operand_infos[d[0]]['optimize'].get('placement_order', 0))
        )
        analyzer = GraphAnalyzer(graph, worker_slots, fixed_assigns, ordered_states, lost_chunks)
        if removes or lost_chunks:
            new_states = analyzer.analyze_state_changes()
            logger.debug('%d chunks lost. %d operands changed state.', len(lost_chunks),
                         len(new_states))

        logger.debug('Start reallocating initial operands')
        new_targets = dict(self._assign_initial_workers(analyzer))

        futures = []
        # make sure that all readies and runnings are included to be checked
        for key, op_info in operand_infos.items():
            if key in new_states:
                continue
            state = op_info['state']
            if state == OperandState.RUNNING and \
                    operand_infos[key]['worker'] not in removes_set:
                continue
            if state in (OperandState.READY, OperandState.RUNNING):
                new_states[key] = state

        for key, state in new_states.items():
            new_target = new_targets.get(key)

            op_info = operand_infos[key]
            from_state = op_info['state']
            # record the target state in special info key
            # in case of concurrency issues
            op_info['failover_state'] = state

            op_ref = self._get_operand_ref(key)
            # states may easily slip into the next state when we are
            # calculating fail-over states. Hence we need to include them
            # into source states.
            if from_state == OperandState.READY:
                from_states = [from_state, OperandState.RUNNING]
            elif from_state == OperandState.RUNNING:
                from_states = [from_state, OperandState.FINISHED]
            elif from_state == OperandState.FINISHED:
                from_states = [from_state, OperandState.FREED]
            else:
                from_states = [from_state]
            futures.append(op_ref.move_failover_state(
                from_states, state, new_target, removes, _tell=True, _wait=False))
        [f.result() for f in futures]

        self._dump_failover_info(adds, removes, lost_chunks, new_states)