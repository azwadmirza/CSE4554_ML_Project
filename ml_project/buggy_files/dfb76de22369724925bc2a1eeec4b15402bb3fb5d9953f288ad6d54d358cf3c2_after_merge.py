    def _emit_duration_stats_for_finished_state(self):
        if self.state == State.RUNNING:
            return
        if self.start_date is None:
            self.log.warning('Failed to record duration of %s: start_date is not set.', self)
            return
        if self.end_date is None:
            self.log.warning('Failed to record duration of %s: end_date is not set.', self)
            return

        duration = self.end_date - self.start_date
        if self.state is State.SUCCESS:
            Stats.timing(f'dagrun.duration.success.{self.dag_id}', duration)
        elif self.state == State.FAILED:
            Stats.timing(f'dagrun.duration.failed.{self.dag_id}', duration)