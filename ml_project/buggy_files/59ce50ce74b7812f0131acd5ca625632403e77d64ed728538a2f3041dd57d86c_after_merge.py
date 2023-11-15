    def _stop_if_finished(self):
        state = self.get_state()
        if state.get_status() == DLSTATUS_SEEDING:
            mode = self.get_seeding_mode()
            if mode == 'never' \
                    or (mode == 'ratio' and state.get_seeding_ratio() >= self.get_seeding_ratio()) \
                    or (mode == 'time' and state.get_seeding_time() >= self.get_seeding_time()):
                self.stop()