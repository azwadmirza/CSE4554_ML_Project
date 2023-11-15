    def find_similar_issues(cls, github_repo, loglines, max_age=timedelta(days=180)):
        """Find similar issues in the GitHub repository."""
        results = dict()
        issues = github_repo.get_issues(state='all', since=datetime.now() - max_age)
        for issue in issues:
            if hasattr(issue, 'pull_request') and issue.pull_request:
                continue
            issue_title = issue.title
            if issue_title.startswith(cls.TITLE_PREFIX):
                issue_title = issue_title[len(cls.TITLE_PREFIX):]

            for logline in loglines:
                log_title = logline.issue_title
                log.debug('Searching for issues similar to: {0}', log_title)

                # Apply diff ratio overrides on first-matched basis, default = 0.9
                diff_ratio = next((override[1] for override in cls.TITLE_DIFF_RATIO_OVERRIDES
                                   if override[0] in log_title.lower()), 0.9)

                if cls.similar(log_title, issue_title, diff_ratio):
                    results[logline.key] = issue

            if len(results) >= len(loglines):
                break

        log.debug('Found {0} similar issues.', len(results))

        return results