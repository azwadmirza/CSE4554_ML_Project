    def reproduce(dvc_dir, cwd=None, **kwargs):
        """Run dvc repro and return the result."""
        from dvc.repo import Repo
        from dvc.repo.experiments import hash_exp

        unchanged = []

        def filter_pipeline(stages):
            unchanged.extend(
                [stage for stage in stages if isinstance(stage, PipelineStage)]
            )

        if cwd:
            old_cwd = os.getcwd()
            os.chdir(cwd)
        else:
            old_cwd = None
            cwd = os.getcwd()

        try:
            logger.debug("Running repro in '%s'", cwd)
            dvc = Repo(dvc_dir)

            # NOTE: for checkpoint experiments we handle persist outs slightly
            # differently than normal:
            #
            # - checkpoint out may not yet exist if this is the first time this
            #   experiment has been run, this is not an error condition for
            #   experiments
            # - at the start of a repro run, we need to remove the persist out
            #   and restore it to its last known (committed) state (which may
            #   be removed/does not yet exist) so that our executor workspace
            #   is not polluted with the (persistent) out from an unrelated
            #   experiment run
            checkpoint = kwargs.pop("checkpoint", False)
            dvc.checkout(
                allow_missing=checkpoint, force=checkpoint, quiet=checkpoint
            )
            stages = dvc.reproduce(
                on_unchanged=filter_pipeline,
                allow_missing=checkpoint,
                **kwargs,
            )
        finally:
            if old_cwd is not None:
                os.chdir(old_cwd)

        # ideally we would return stages here like a normal repro() call, but
        # stages is not currently picklable and cannot be returned across
        # multiprocessing calls
        return hash_exp(stages + unchanged)