def _run_callback(stage, callback_func):
    stage.save(allow_missing=True)
    stage.commit(allow_missing=True)
    for out in stage.outs:
        if not out.use_scm_ignore and out.is_in_repo:
            stage.repo.scm.track_file(os.fspath(out.path_info))
    stage.repo.scm.track_changed_files()
    logger.debug("Running checkpoint callback for stage '%s'", stage)
    callback_func()