    def log(self) -> None:
        if not self.measurements:
            log.debug(
                "Idle", context_switches=self.context_switches, measurements=self.measurements
            )
            return
        log.debug(
            "Idle",
            start=self.measurements_start,
            context_switches=self.context_switches,
            idled=self.idled,
            interval=self.running_interval,
            idle_pct=self.idled_pct,
            measurements=self.measurements,
        )