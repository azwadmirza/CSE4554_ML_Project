def launch(
    launcher: RayAWSLauncher,
    job_overrides: Sequence[Sequence[str]],
    initial_job_idx: int,
) -> Sequence[JobReturn]:
    setup_globals()
    assert launcher.config is not None
    assert launcher.config_loader is not None
    assert launcher.task_function is not None

    setup_commands = launcher.env_setup.commands
    with read_write(setup_commands):
        setup_commands.extend(
            [
                f"pip install {package}=={version}"
                for package, version in launcher.env_setup.pip_packages.items()
            ]
        )
        setup_commands.extend(launcher.ray_cfg.cluster.setup_commands)

    with read_write(launcher.ray_cfg.cluster):
        launcher.ray_cfg.cluster.setup_commands = setup_commands

    configure_log(launcher.config.hydra.hydra_logging, launcher.config.hydra.verbose)

    log.info(f"Ray Launcher is launching {len(job_overrides)} jobs, ")

    with tempfile.TemporaryDirectory() as local_tmp_dir:
        sweep_configs = []
        for idx, overrides in enumerate(job_overrides):
            idx = initial_job_idx + idx
            ostr = " ".join(filter_overrides(overrides))
            log.info(f"\t#{idx} : {ostr}")
            sweep_config = launcher.config_loader.load_sweep_config(
                launcher.config, list(overrides)
            )
            with open_dict(sweep_config):
                # job.id will be set on the EC2 instance before running the job.
                sweep_config.hydra.job.num = idx

            sweep_configs.append(sweep_config)

        _pickle_jobs(
            tmp_dir=local_tmp_dir,
            sweep_configs=sweep_configs,  # type: ignore
            task_function=launcher.task_function,
            singleton_state=Singleton.get_state(),
        )

        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
            with open(f.name, "w") as file:
                OmegaConf.save(
                    config=launcher.ray_cfg.cluster, f=file.name, resolve=True
                )
            launcher.ray_yaml_path = f.name
            log.info(
                f"Saving RayClusterConf in a temp yaml file: {launcher.ray_yaml_path}."
            )

            return launch_jobs(
                launcher, local_tmp_dir, Path(launcher.config.hydra.sweep.dir)
            )