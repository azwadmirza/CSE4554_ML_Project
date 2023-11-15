def _run_toplevel(config, config_file, work_dir, parallel,
                  fc_dir=None, run_info_yaml=None):
    """
    Run toplevel analysis, processing a set of input files.
    config_file -- Main YAML configuration file with system parameters
    fc_dir -- Directory of fastq files to process
    run_info_yaml -- YAML configuration file specifying inputs to process
    """
    parallel = log.create_base_logger(config, parallel)
    log.setup_local_logging(config, parallel)
    logger.info("System YAML configuration: %s" % os.path.abspath(config_file))
    dirs = run_info.setup_directories(work_dir, fc_dir, config, config_file)
    config_file = os.path.join(dirs["config"], os.path.basename(config_file))
    pipelines, config = _pair_samples_with_pipelines(run_info_yaml, config)
    system.write_info(dirs, parallel, config)
    with tx_tmpdir(config if parallel.get("type") == "local" else None) as tmpdir:
        tempfile.tempdir = tmpdir
        for pipeline, samples in pipelines.items():
            for xs in pipeline(config, run_info_yaml, parallel, dirs, samples):
                pass