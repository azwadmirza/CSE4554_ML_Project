    async def get_full_sha1(self, rev: str) -> str:
        """
        Gets full sha1 object name.

        Parameters
        ----------
        rev : str
            Revision to search for full sha1 object name.

        Raises
        ------
        .UnknownRevision
            When git cannot find provided revision.
        .AmbiguousRevision
            When git cannot resolve provided short sha1 to one commit.

        Returns
        -------
        `str`
            Full sha1 object name for provided revision.

        """
        git_command = ProcessFormatter().format(
            self.GIT_GET_FULL_SHA1, path=self.folder_path, rev=rev
        )
        p = await self._run(git_command)

        if p.returncode != 0:
            stderr = p.stderr.decode(**DECODE_PARAMS).strip()
            ambiguous_error = f"error: short SHA1 {rev} is ambiguous\nhint: The candidates are:\n"
            if not stderr.startswith(ambiguous_error):
                raise errors.UnknownRevision(f"Revision {rev} cannot be found.", git_command)
            candidates = []
            for match in self.AMBIGUOUS_ERROR_REGEX.finditer(stderr, len(ambiguous_error)):
                candidates.append(Candidate(match["rev"], match["type"], match["desc"]))
            if candidates:
                raise errors.AmbiguousRevision(
                    f"Short SHA1 {rev} is ambiguous.", git_command, candidates
                )
            raise errors.UnknownRevision(f"Revision {rev} cannot be found.", git_command)

        return p.stdout.decode(**DECODE_PARAMS).strip()