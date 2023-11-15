    def _prepare_for_stage(self, stage: str):
        utils.set_global_seed(self.experiment.initial_seed)
        migrating_params = {}
        stage_state_params = self.experiment.get_state_params(stage)
        migrate_from_previous_stage = \
            stage_state_params.get("migrate_from_previous_stage", True)
        if self.state is not None and migrate_from_previous_stage:
            migrating_params.update(
                {
                    "step": self.state.step,
                    "epoch": self.state.epoch
                }
            )

        utils.set_global_seed(self.experiment.initial_seed)
        self.model, criterion, optimizer, scheduler, self.device = \
            self._get_experiment_components(stage)

        utils.set_global_seed(self.experiment.initial_seed)
        self.state = self.state_fn(
            stage=stage,
            model=self.model,
            device=self.device,
            criterion=criterion,
            optimizer=optimizer,
            scheduler=scheduler,
            **stage_state_params,
            **migrating_params
        )

        utils.set_global_seed(self.experiment.initial_seed)
        callbacks = self.experiment.get_callbacks(stage)

        loggers = utils.process_callbacks(
            OrderedDict(
                [
                    (k, v) for k, v in callbacks.items()
                    if isinstance(v, LoggerCallback)
                ]
            )
        )
        callbacks = utils.process_callbacks(
            OrderedDict(
                [
                    (k, v) for k, v in callbacks.items()
                    if not isinstance(v, LoggerCallback)
                ]
            )
        )

        self.state.loggers = loggers
        self.loggers = loggers
        self.callbacks = callbacks