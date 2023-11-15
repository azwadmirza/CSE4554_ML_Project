def launch(
    launcher: JoblibLauncher,
    job_overrides: Sequence[Sequence[str]],
    initial_job_idx: int,
) -> Sequence[JobReturn]:
    """
    :param job_overrides: a List of List<String>, where each inner list is the arguments for one job run.
    :param initial_job_idx: Initial job idx in batch.
    :return: an array of return values from run_job with indexes corresponding to the input list indexes.
    """
    setup_globals()
    assert launcher.config is not None
    assert launcher.config_loader is not None
    assert launcher.task_function is not None

    configure_log(launcher.config.hydra.hydra_logging, launcher.config.hydra.verbose)
    sweep_dir = Path(str(launcher.config.hydra.sweep.dir))
    sweep_dir.mkdir(parents=True, exist_ok=True)

    # Joblib's backend is hard-coded to loky since the threading
    # backend is incompatible with Hydra
    joblib_cfg = launcher.joblib
    joblib_cfg["backend"] = "loky"

    log.info(
        "Joblib.Parallel({}) is launching {} jobs".format(
            ",".join([f"{k}={v}" for k, v in joblib_cfg.items()]),
            len(job_overrides),
        )
    )
    log.info("Launching jobs, sweep output dir : {}".format(sweep_dir))
    for idx, overrides in enumerate(job_overrides):
        log.info("\t#{} : {}".format(idx, " ".join(filter_overrides(overrides))))

    singleton_state = Singleton.get_state()

    runs = Parallel(**joblib_cfg)(
        delayed(execute_job)(
            initial_job_idx + idx,
            overrides,
            launcher.config_loader,
            launcher.config,
            launcher.task_function,
            singleton_state,
        )
        for idx, overrides in enumerate(job_overrides)
    )

    assert isinstance(runs, List)
    for run in runs:
        assert isinstance(run, JobReturn)
    return runs