    def _emit_duration_stats_for_finished_state(self):
        if self.state == State.RUNNING:
            return

        duration = self.end_date - self.start_date
        if self.state is State.SUCCESS:
            Stats.timing(f'dagrun.duration.success.{self.dag_id}', duration)
        elif self.state == State.FAILED:
            Stats.timing(f'dagrun.duration.failed.{self.dag_id}', duration)