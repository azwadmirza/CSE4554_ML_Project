    def scan_diff(
        self,
        diff,
        baseline_filename='',
        last_commit_hash='',
        repo_name='',
    ):
        """For optimization purposes, our scanning strategy focuses on looking
        at incremental differences, rather than re-scanning the codebase every time.
        This function supports this, and adds information to self.data.

        :type diff: str
        :param diff: diff string.
                     Eg. The output of `git diff <fileA> <fileB>`

        :type baseline_filename: str
        :param baseline_filename: if there are any baseline secrets, then the baseline
                                  file will have hashes in them. By specifying it, we
                                  can skip this clear exception.

        :type last_commit_hash: str
        :param last_commit_hash: used for logging only -- the last commit hash we saved

        :type repo_name: str
        :param repo_name: used for logging only -- the name of the repo
        """
        try:
            patch_set = PatchSet.from_string(diff)
        except UnidiffParseError:  # pragma: no cover
            alert = {
                'alert': 'UnidiffParseError',
                'hash': last_commit_hash,
                'repo_name': repo_name,
            }
            log.error(alert)
            raise

        if self.exclude_regex:
            regex = re.compile(self.exclude_regex, re.IGNORECASE)

        for patch_file in patch_set:
            filename = patch_file.path
            # If the file matches the exclude_regex, we skip it
            if self.exclude_regex and regex.search(filename):
                continue

            if filename == baseline_filename:
                continue

            for results, plugin in self._results_accumulator(filename):
                results.update(
                    self._extract_secrets_from_patch(
                        patch_file,
                        plugin,
                        filename,
                    ),
                )