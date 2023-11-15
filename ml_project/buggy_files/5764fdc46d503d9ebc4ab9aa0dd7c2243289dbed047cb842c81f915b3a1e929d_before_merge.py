    def stop(self):
        if self.show_spin:
            self._stop_running.set()
            self._spinner_thread.join()