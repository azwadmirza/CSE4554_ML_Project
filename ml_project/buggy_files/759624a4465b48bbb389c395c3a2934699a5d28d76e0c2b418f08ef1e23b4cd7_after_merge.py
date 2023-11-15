    def main_loop(self):
        try:
            with self.pool:
                try:
                    self.start()
                    self._running = True
                    while True:
                        self.pool.join(1)
                        stopped = []
                        for idx, proc in enumerate(self.pool.processes):
                            if not proc.is_alive():
                                stopped.append(idx)
                        if stopped:
                            self.handle_process_down(stopped)
                except:
                    self._running = False
                    self.stop()
        finally:
            self._running = False