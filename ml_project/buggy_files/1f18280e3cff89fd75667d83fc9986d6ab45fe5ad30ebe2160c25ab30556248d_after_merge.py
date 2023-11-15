    def commit(
        cls,
        scm: "Git",
        exp_hash: str,
        exp_name: Optional[str] = None,
        force: bool = False,
        checkpoint: bool = False,
    ):
        """Commit stages as an experiment and return the commit SHA."""
        rev = scm.get_rev()
        if not scm.is_dirty(untracked_files=True):
            logger.debug("No changes to commit")
            raise UnchangedExperimentError(rev)

        branch = scm.get_ref(EXEC_BRANCH, follow=False)
        if branch:
            old_ref = rev
            logger.debug("Commit to current experiment branch '%s'", branch)
        else:
            baseline_rev = scm.get_ref(EXEC_BASELINE)
            name = exp_name if exp_name else f"exp-{exp_hash[:5]}"
            ref_info = ExpRefInfo(baseline_rev, name)
            branch = str(ref_info)
            old_ref = None
            if not force and scm.get_ref(branch):
                if checkpoint:
                    raise CheckpointExistsError(ref_info.name)
                raise ExperimentExistsError(ref_info.name)
            logger.debug("Commit to new experiment branch '%s'", branch)

        scm.gitpython.repo.git.add(update=True)
        scm.commit(f"dvc: commit experiment {exp_hash}", no_verify=True)
        new_rev = scm.get_rev()
        scm.set_ref(branch, new_rev, old_ref=old_ref)
        scm.set_ref(EXEC_BRANCH, branch, symbolic=True)
        if checkpoint:
            scm.set_ref(EXEC_CHECKPOINT, new_rev)
        return new_rev