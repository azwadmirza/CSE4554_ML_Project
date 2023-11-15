    def _pre_experiment_hook(self, experiment: Experiment):
        monitoring_params = experiment.monitoring_params
        monitoring_params["dir"] = str(Path(experiment.logdir).absolute())

        log_on_batch_end: bool = \
            monitoring_params.pop("log_on_batch_end", False)
        log_on_epoch_end: bool = \
            monitoring_params.pop("log_on_epoch_end", True)
        checkpoints_glob: List[str] = \
            monitoring_params.pop("checkpoints_glob", [])
        self._init(
            log_on_batch_end=log_on_batch_end,
            log_on_epoch_end=log_on_epoch_end,
            checkpoints_glob=checkpoints_glob,
        )
        if isinstance(experiment, ConfigExperiment):
            exp_config = utils.flatten_dict(experiment.stages_config)
            wandb.init(**monitoring_params, config=exp_config)
        else:
            wandb.init(**monitoring_params)