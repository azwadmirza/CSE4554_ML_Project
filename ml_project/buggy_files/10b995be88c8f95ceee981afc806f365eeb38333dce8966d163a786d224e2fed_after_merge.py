    def _stash_exp(self, *args, params: Optional[dict] = None, **kwargs):
        """Stash changes from the current (parent) workspace as an experiment.

        Args:
            params: Optional dictionary of parameter values to be used.
                Values take priority over any parameters specified in the
                user's workspace.
        """
        rev = self.scm.get_rev()

        # patch user's workspace into experiments clone
        tmp = tempfile.NamedTemporaryFile(delete=False).name
        try:
            self.repo.scm.repo.git.diff(
                patch=True, full_index=True, binary=True, output=tmp
            )
            if os.path.getsize(tmp):
                logger.debug("Patching experiment workspace")
                self.scm.repo.git.apply(tmp)
            elif not params:
                # experiment matches original baseline
                raise UnchangedExperimentError(rev)
        finally:
            remove(tmp)

        # update experiment params from command line
        if params:
            self._update_params(params)

        # save additional repro command line arguments
        self._pack_args(*args, **kwargs)

        # save experiment as a stash commit w/message containing baseline rev
        # (stash commits are merge commits and do not contain a parent commit
        # SHA)
        msg = f"{self.STASH_MSG_PREFIX}{rev}"
        self.scm.repo.git.stash("push", "-m", msg)
        return self.scm.resolve_rev("stash@{0}")