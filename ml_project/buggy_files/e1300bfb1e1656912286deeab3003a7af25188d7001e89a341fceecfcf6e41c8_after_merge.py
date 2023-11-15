def run_job(
    config: DictConfig,
    task_function: TaskFunction,
    job_dir_key: str,
    job_subdir_key: Optional[str],
) -> "JobReturn":
    old_cwd = os.getcwd()
    working_dir = str(OmegaConf.select(config, job_dir_key))
    if job_subdir_key is not None:
        # evaluate job_subdir_key lazily.
        # this is running on the client side in sweep and contains things such as job:id which
        # are only available there.
        subdir = str(OmegaConf.select(config, job_subdir_key))
        working_dir = os.path.join(working_dir, subdir)
    try:
        ret = JobReturn()
        ret.working_dir = working_dir
        task_cfg = copy.deepcopy(config)
        del task_cfg["hydra"]
        ret.cfg = task_cfg
        ret.hydra_cfg = OmegaConf.create({"hydra": HydraConfig.get()})
        overrides = OmegaConf.to_container(config.hydra.overrides.task)
        assert isinstance(overrides, list)
        ret.overrides = overrides
        # handle output directories here
        Path(str(working_dir)).mkdir(parents=True, exist_ok=True)
        os.chdir(working_dir)
        hydra_output = Path(config.hydra.output_subdir)

        configure_log(config.hydra.job_logging, config.hydra.verbose)

        hydra_cfg = OmegaConf.masked_copy(config, "hydra")
        assert isinstance(hydra_cfg, DictConfig)

        _save_config(task_cfg, "config.yaml", hydra_output)
        _save_config(hydra_cfg, "hydra.yaml", hydra_output)
        _save_config(config.hydra.overrides.task, "overrides.yaml", hydra_output)
        ret.return_value = task_function(task_cfg)
        ret.task_name = JobRuntime.instance().get("name")

        # shut down logging to ensure job log files are closed.
        # If logging is still required after run_job caller is responsible to re-initialize it.
        logging.shutdown()

        return ret
    finally:
        os.chdir(old_cwd)