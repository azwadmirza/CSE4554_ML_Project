    def submit_github_issue(self, version_checker, max_issues=500):
        """Submit errors to github.

        :param version_checker:
        :type version_checker: CheckVersion
        :param max_issues:
        :type max_issues: int
        :return: user message and issue number
        :rtype: list of tuple(str, str)
        """
        if not sickbeard.DEBUG or not sickbeard.GIT_USERNAME or not sickbeard.GIT_PASSWORD:
            logger.warning(IssueSubmitter.INVALID_CONFIG)
            return [(IssueSubmitter.INVALID_CONFIG, None)]

        if not ErrorViewer.errors:
            logger.info(IssueSubmitter.NO_ISSUES)
            return [(IssueSubmitter.NO_ISSUES, None)]

        if not sickbeard.DEVELOPER and version_checker.need_update():
            logger.warning(IssueSubmitter.UNSUPPORTED_VERSION)
            return [(IssueSubmitter.UNSUPPORTED_VERSION, None)]

        if self.running:
            logger.warning(IssueSubmitter.ALREADY_RUNNING)
            return [(IssueSubmitter.ALREADY_RUNNING, None)]

        self.running = True
        try:
            github = Github(login_or_token=sickbeard.GIT_USERNAME, password=sickbeard.GIT_PASSWORD, user_agent='Medusa')
            github_repo = github.get_organization(sickbeard.GIT_ORG).get_repo(sickbeard.GIT_REPO)
            loglines = ErrorViewer.errors[:max_issues]
            similar_issues = IssueSubmitter.find_similar_issues(github_repo, loglines)

            return IssueSubmitter.submit_issues(github, github_repo, loglines, similar_issues)
        except BadCredentialsException:
            logger.warning(IssueSubmitter.BAD_CREDENTIALS)
            return [(IssueSubmitter.BAD_CREDENTIALS, None)]
        except RateLimitExceededException:
            logger.warning(IssueSubmitter.RATE_LIMIT)
            return [(IssueSubmitter.RATE_LIMIT, None)]
        finally:
            self.running = False