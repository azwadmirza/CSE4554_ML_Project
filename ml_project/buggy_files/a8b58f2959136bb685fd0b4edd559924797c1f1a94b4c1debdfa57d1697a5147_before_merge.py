    def run(
        self,
        config_name: Optional[str],
        task_function: TaskFunction,
        overrides: List[str],
        with_log_configuration: bool = True,
    ) -> JobReturn:
        cfg = self.compose_config(
            config_name=config_name,
            overrides=overrides,
            with_log_configuration=with_log_configuration,
            run_mode=RunMode.RUN,
        )
        HydraConfig.instance().set_config(cfg)

        return run_job(
            config=cfg,
            task_function=task_function,
            job_dir_key="hydra.run.dir",
            job_subdir_key=None,
            configure_logging=with_log_configuration,
        )