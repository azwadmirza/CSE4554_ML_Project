    def stop(self):
        return self._node.safe_stop_looping_call(self._process_lc)