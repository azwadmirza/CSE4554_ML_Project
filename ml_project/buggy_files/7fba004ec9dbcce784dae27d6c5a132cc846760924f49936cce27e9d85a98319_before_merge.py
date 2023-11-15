    def _run_stage(self, stage: str):
        self._prepare_for_stage(stage)

        self._run_event("stage", moment="start")
        for epoch in range(self.state.num_epochs):
            self.state.stage_epoch = epoch

            self._run_event("epoch", moment="start")
            self._run_epoch(stage=stage, epoch=epoch)
            self._run_event("epoch", moment="end")

            if self._check_run and self.state.stage_epoch >= 2:
                break
            if self.state.early_stop:
                self.state.early_stop = False
                break

            self.state.epoch += 1
        self._run_event("stage", moment="end")