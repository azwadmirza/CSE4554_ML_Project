    def add_finished_terminal(self, op_key, final_state=None, exc=None):
        """
        Add a terminal operand to finished set. Calling this method
        will change graph state if all terminals are in finished states.
        :param op_key: operand key
        :param final_state: state of the operand
        """
        if self._state not in (GraphState.RUNNING, GraphState.CANCELLING):
            return
        if exc is not None:
            self._graph_meta_ref.set_exc_info(exc, _tell=True, _wait=False)

        tileable_keys = self._terminal_chunk_op_key_to_tileable_key[op_key]
        is_failed = final_state in (GraphState.CANCELLED, GraphState.FAILED)
        terminal_tileable_count = len(self._terminal_tileable_key_to_chunk_op_keys)
        try:
            for tileable_key in tileable_keys:
                self._target_tileable_finished[tileable_key].add(op_key)
                if final_state == GraphState.FAILED:
                    if self.final_state != GraphState.CANCELLED:
                        self.final_state = GraphState.FAILED
                elif final_state == GraphState.CANCELLED:
                    self.final_state = final_state

                if self._target_tileable_finished[tileable_key] == \
                        self._terminal_tileable_key_to_chunk_op_keys[tileable_key]:
                    self._terminated_tileable_keys.add(tileable_key)
                    self._all_terminated_tileable_keys.add(tileable_key)
                    if not is_failed and len(self._terminated_tileable_keys) == terminal_tileable_count:
                        # update shape if tileable or its chunks have unknown shape
                        self._update_tileable_and_its_chunk_shapes()
        except:
            for tileable_key in tileable_keys:
                self._target_tileable_finished[tileable_key].remove(op_key)
            raise

        terminated_chunks = self._op_key_to_chunk[op_key]
        self._terminated_chunk_keys.update([c.key for c in terminated_chunks
                                            if c.key in self._terminal_chunk_keys])
        if self._terminated_chunk_keys == self._terminal_chunk_keys:
            if self._chunk_graph_builder.done or is_failed:
                if self._chunk_graph_builder.prev_tileable_graph is not None:
                    # if failed before, clear intermediate data
                    to_free_tileable_keys = \
                        self._all_terminated_tileable_keys - set(self._target_tileable_keys)
                    skip_chunk_keys = set()
                    for target_tileable_data in self._target_tileable_datas:
                        tiled_target_tileable_data = \
                            self._tileable_key_opid_to_tiled[target_tileable_data.key,
                                                             target_tileable_data.op.id][-1]
                        skip_chunk_keys.update([c.key for c in tiled_target_tileable_data.chunks])
                    [self.free_tileable_data(k, skip_chunk_keys=skip_chunk_keys)
                     for k in to_free_tileable_keys]
                self.state = self.final_state if self.final_state is not None else GraphState.SUCCEEDED
                self._graph_meta_ref.set_graph_end(_tell=True)
            else:
                self._execute_graph(compose=self._chunk_graph_builder.is_compose)