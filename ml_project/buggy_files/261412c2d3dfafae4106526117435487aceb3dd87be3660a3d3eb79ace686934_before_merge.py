    def _execute_graph(self, compose=True):
        try:
            self.prepare_graph(compose=compose)
            self._detect_cancel()

            self._dump_graph()

            self.analyze_graph()
            self._detect_cancel()

            self.create_operand_actors()
            self._detect_cancel(self.stop_graph)
        except ExecutionInterrupted:
            pass
        except:  # noqa: E722
            logger.exception('Failed to start graph execution.')
            self._graph_meta_ref.set_exc_info(sys.exc_info(), _tell=True, _wait=False)
            self.stop_graph()
            self.state = GraphState.FAILED
            self._graph_meta_ref.set_graph_end(_tell=True, _wait=False)
            raise

        if len(self._chunk_graph_cache) == 0:
            self.state = GraphState.SUCCEEDED
            self._graph_meta_ref.set_graph_end(_tell=True, _wait=False)