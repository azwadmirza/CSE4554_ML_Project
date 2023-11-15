    def execute_graph(self):
        """
        Start graph execution
        """
        def _detect_cancel(callback=None):
            if self.reload_state() == GraphState.CANCELLING:
                logger.info('Cancel detected, stopping')
                if callback:
                    callback()
                else:
                    self._end_time = time.time()
                    self.state = GraphState.CANCELLED
                raise ExecutionInterrupted

        self._start_time = time.time()
        self.state = GraphState.PREPARING

        try:
            self.prepare_graph()
            _detect_cancel()

            self.scan_node()
            _detect_cancel()

            self.place_initial_chunks()
            _detect_cancel()

            self.create_operand_actors()
            _detect_cancel(self.stop_graph)
        except ExecutionInterrupted:
            pass
        except:  # noqa: E722
            logger.exception('Failed to start graph execution.')
            self.stop_graph()
            self.state = GraphState.FAILED
            raise