    def _stop_if_finished(self):
        if self.get_state().get_status() == DLSTATUS_SEEDING:
            mode = self.get_seeding_mode()
            if mode == 'never' \
                    or (mode == 'ratio' and self.get_all_time_ratio() >= self.get_seeding_ratio()) \
                    or (mode == 'time' and self.get_finished_time() >= self.get_seeding_time()):
                self.stop()