def _run_callback(stage, callback_func):
    stage.save(allow_missing=True)
    stage.commit(allow_missing=True)
    logger.debug("Running checkpoint callback for stage '%s'", stage)
    callback_func()