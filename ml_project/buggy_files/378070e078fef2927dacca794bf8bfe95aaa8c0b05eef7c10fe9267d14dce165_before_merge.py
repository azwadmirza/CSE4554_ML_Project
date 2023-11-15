def _reproduce_stage(stage, **kwargs):
    def _run_callback(repro_callback):
        _dump_stage(stage)
        repro_callback([stage])

    checkpoint_func = kwargs.pop("checkpoint_func", None)
    if stage.is_checkpoint:
        if checkpoint_func:
            kwargs["checkpoint_func"] = partial(_run_callback, checkpoint_func)
        else:
            logger.warning(
                "Checkpoint stages are not fully supported in 'dvc repro'. "
                "Checkpoint stages should be reproduced with 'dvc exp run' "
                "or 'dvc exp resume'."
            )

    if stage.frozen and not stage.is_import:
        logger.warning(
            "{} is frozen. Its dependencies are"
            " not going to be reproduced.".format(stage)
        )

    stage = stage.reproduce(**kwargs)
    if not stage:
        return []

    if not kwargs.get("dry", False):
        _dump_stage(stage)

    return [stage]