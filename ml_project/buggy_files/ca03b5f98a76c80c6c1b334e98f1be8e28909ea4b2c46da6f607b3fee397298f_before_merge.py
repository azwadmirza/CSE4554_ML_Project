    def multirun(
        self,
        config_name: Optional[str],
        task_function: TaskFunction,
        overrides: List[str],
        with_log_configuration: bool = True,
    ) -> Any:
        # Initial config is loaded without strict (individual job configs may have strict).
        cfg = self.compose_config(
            config_name=config_name,
            overrides=overrides,
            strict=False,
            with_log_configuration=with_log_configuration,
            run_mode=RunMode.MULTIRUN,
        )
        HydraConfig.instance().set_config(cfg)

        sweeper = Plugins.instance().instantiate_sweeper(
            config=cfg, config_loader=self.config_loader, task_function=task_function
        )
        task_overrides = OmegaConf.to_container(cfg.hydra.overrides.task, resolve=False)
        assert isinstance(task_overrides, list)
        return sweeper.sweep(arguments=task_overrides)