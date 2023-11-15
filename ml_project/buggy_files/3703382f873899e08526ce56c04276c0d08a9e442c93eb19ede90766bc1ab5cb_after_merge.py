    def commit(self, msg: str, no_verify: bool = False):
        from dulwich.errors import CommitError
        from dulwich.porcelain import commit

        try:
            commit(self.root_dir, message=msg, no_verify=no_verify)
        except CommitError as exc:
            raise SCMError("Git commit failed") from exc