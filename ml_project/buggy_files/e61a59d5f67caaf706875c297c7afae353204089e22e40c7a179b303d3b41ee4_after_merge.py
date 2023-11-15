    def commit(self, msg: str, no_verify: bool = False):
        from git.exc import HookExecutionError

        try:
            self.repo.index.commit(msg, skip_hooks=no_verify)
        except HookExecutionError as exc:
            raise SCMError("Git pre-commit hook failed") from exc