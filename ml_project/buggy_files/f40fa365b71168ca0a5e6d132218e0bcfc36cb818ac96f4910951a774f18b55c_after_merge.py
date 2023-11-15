def launch_jobs(
    launcher: RayAWSLauncher, local_tmp_dir: str, sweep_dir: Path
) -> Sequence[JobReturn]:
    ray_up(launcher.ray_yaml_path)
    with tempfile.TemporaryDirectory() as local_tmp_download_dir:

        with ray_tmp_dir(
            launcher.ray_yaml_path, launcher.ray_cfg.run_env.name
        ) as remote_tmp_dir:

            ray_rsync_up(
                launcher.ray_yaml_path, os.path.join(local_tmp_dir, ""), remote_tmp_dir
            )

            script_path = os.path.join(os.path.dirname(__file__), "_remote_invoke.py")
            remote_script_path = os.path.join(remote_tmp_dir, "_remote_invoke.py")
            ray_rsync_up(launcher.ray_yaml_path, script_path, remote_script_path)

            if launcher.sync_up.source_dir:
                source_dir = _get_abs_code_dir(launcher.sync_up.source_dir)
                target_dir = (
                    launcher.sync_up.target_dir
                    if launcher.sync_up.target_dir
                    else remote_tmp_dir
                )
                rsync(
                    launcher.ray_yaml_path,
                    launcher.sync_up.include,
                    launcher.sync_up.exclude,
                    os.path.join(source_dir, ""),
                    target_dir,
                )

            ray_exec(
                launcher.ray_yaml_path,
                launcher.ray_cfg.run_env.name,
                remote_script_path,
                remote_tmp_dir,
            )

            ray_rsync_down(
                launcher.ray_yaml_path,
                os.path.join(remote_tmp_dir, JOB_RETURN_PICKLE),
                local_tmp_download_dir,
            )

            sync_down_cfg = launcher.sync_down

            if (
                sync_down_cfg.target_dir
                or sync_down_cfg.source_dir
                or sync_down_cfg.include
                or sync_down_cfg.exclude
            ):
                source_dir = (
                    sync_down_cfg.source_dir if sync_down_cfg.source_dir else sweep_dir
                )
                target_dir = (
                    sync_down_cfg.source_dir if sync_down_cfg.source_dir else sweep_dir
                )
                target_dir = Path(_get_abs_code_dir(target_dir))
                target_dir.mkdir(parents=True, exist_ok=True)

                rsync(
                    launcher.ray_yaml_path,
                    launcher.sync_down.include,
                    launcher.sync_down.exclude,
                    os.path.join(source_dir),
                    str(target_dir),
                    up=False,
                )
                log.info(
                    f"Syncing outputs from remote dir: {source_dir} to local dir: {target_dir.absolute()} "
                )

        if launcher.stop_cluster:
            log.info("Stopping cluster now. (stop_cluster=true)")
            if launcher.ray_cfg.cluster.provider.cache_stopped_nodes:
                log.info("NOT deleting the cluster (provider.cache_stopped_nodes=true)")
            else:
                log.info("Deleted the cluster (provider.cache_stopped_nodes=false)")
            ray_down(launcher.ray_yaml_path)
        else:
            log.warning(
                "NOT stopping cluster, this may incur extra cost for you. (stop_cluster=false)"
            )

        with open(os.path.join(local_tmp_download_dir, JOB_RETURN_PICKLE), "rb") as f:
            job_returns = pickle.load(f)  # nosec
            assert isinstance(job_returns, List)
            for run in job_returns:
                assert isinstance(run, JobReturn)
            return job_returns