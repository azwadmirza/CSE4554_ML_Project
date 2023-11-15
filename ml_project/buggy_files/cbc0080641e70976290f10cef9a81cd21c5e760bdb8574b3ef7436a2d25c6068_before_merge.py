    def multirun(self, config_file, task_function, overrides):
        # Initial config is loaded without strict (individual job configs may have strict).
        cfg = self.compose_config(
            config_file=config_file,
            overrides=overrides,
            strict=False,
            with_log_configuration=True,
        )
        HydraConfig().set_config(cfg)
        sweeper = Plugins.instantiate_sweeper(
            config=cfg, config_loader=self.config_loader, task_function=task_function,
        )
        task_overrides = cfg.hydra.overrides.task
        return sweeper.sweep(arguments=task_overrides)