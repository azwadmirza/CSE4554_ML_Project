    def submit_github_issue(self, version_checker, max_issues=500):
        """Submit errors to github."""
        def result(message, level=logging.WARNING):
            log.log(level, message)
            return [(message, None)]

        if not app.DEBUG:
            return result(self.DEBUG_NOT_ENABLED)

        if app.GIT_AUTH_TYPE == 1 and not app.GIT_TOKEN:
            return result(self.MISSING_CREDENTIALS_TOKEN)

        if app.GIT_AUTH_TYPE == 0 and not (app.GIT_USERNAME and app.GIT_PASSWORD):
            return result(self.MISSING_CREDENTIALS)

        if not ErrorViewer.errors:
            return result(self.NO_ISSUES, logging.INFO)

        if not app.DEVELOPER and version_checker.need_update():
            return result(self.UNSUPPORTED_VERSION)

        if self.running:
            return result(self.ALREADY_RUNNING)

        self.running = True
        try:
            if app.GIT_AUTH_TYPE:
                github = token_authenticate(app.GIT_TOKEN)
            else:
                github = authenticate(app.GIT_USERNAME, app.GIT_PASSWORD)
            if not github:
                return result(self.BAD_CREDENTIALS)

            github_repo = get_github_repo(app.GIT_ORG, app.GIT_REPO, gh=github)
            loglines = ErrorViewer.errors[:max_issues]
            similar_issues = self.find_similar_issues(github_repo, loglines)

            return self.submit_issues(github, github_repo, loglines, similar_issues)
        except RateLimitExceededException:
            return result(self.RATE_LIMIT)
        except (GithubException, IOError) as error:
            log.debug('Issue submitter failed with error: {0!r}', error)
            # If the api return http status 404, authentication or permission issue(token right to create gists)
            if isinstance(error, UnknownObjectException):
                return result(self.GITHUB_UNKNOWNOBJECTEXCEPTION)
            return result(self.GITHUB_EXCEPTION)
        finally:
            self.running = False