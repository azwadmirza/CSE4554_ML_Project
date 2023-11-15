    def unpause(self):
        """Restart tqdm timer from last print time."""
        cur_t = self._time()
        self.start_t += cur_t - self.last_print_t
        self.last_print_t = cur_t