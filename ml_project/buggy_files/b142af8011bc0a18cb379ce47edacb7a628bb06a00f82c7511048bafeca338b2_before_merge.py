    def reproduce(
        cls,
        dvc_dir: str,
        queue: "Queue",
        rev: str,
        cwd: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Tuple[Optional[str], bool]:
        """Run dvc repro and return the result.

        Returns tuple of (exp_hash, force) where exp_hash is the experiment
            hash (or None on error) and force is a bool specifying whether or
            not this experiment should force overwrite any existing duplicates.
        """
        from dvc.repo.checkout import checkout as dvc_checkout
        from dvc.repo.reproduce import reproduce as dvc_reproduce

        unchanged = []

        queue.put((rev, os.getpid()))

        def filter_pipeline(stages):
            unchanged.extend(
                [stage for stage in stages if isinstance(stage, PipelineStage)]
            )

        result: Optional[str] = None
        repro_force: bool = False

        try:
            dvc = Repo(dvc_dir)
            old_cwd = os.getcwd()
            new_cwd = cwd if cwd else dvc.root_dir
            os.chdir(new_cwd)
            logger.debug("Running repro in '%s'", cwd)

            args_path = os.path.join(
                dvc.tmp_dir, BaseExecutor.PACKED_ARGS_FILE
            )
            if os.path.exists(args_path):
                args, kwargs = BaseExecutor.unpack_repro_args(args_path)
                remove(args_path)
            else:
                args = []
                kwargs = {}

            repro_force = kwargs.get("force", False)

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
            dvc_checkout(dvc, force=True, quiet=True)

            checkpoint_func = partial(cls.checkpoint_callback, dvc.scm, name)
            stages = dvc_reproduce(
                dvc,
                *args,
                on_unchanged=filter_pipeline,
                checkpoint_func=checkpoint_func,
                **kwargs,
            )

            exp_hash = cls.hash_exp(stages)
            result = exp_hash
            exp_rev = cls.commit(dvc.scm, exp_hash, exp_name=name)
            if dvc.scm.get_ref(EXEC_CHECKPOINT):
                dvc.scm.set_ref(EXEC_CHECKPOINT, exp_rev)
        except UnchangedExperimentError:
            pass
        finally:
            if dvc:
                dvc.scm.close()
            if old_cwd:
                os.chdir(old_cwd)

        # ideally we would return stages here like a normal repro() call, but
        # stages is not currently picklable and cannot be returned across
        # multiprocessing calls
        return result, repro_force