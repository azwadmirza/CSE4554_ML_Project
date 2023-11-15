    def list_remote_branches():
        try:
            gh = get_github_repo(app.GIT_ORG, app.GIT_REPO)
            return [x.name for x in gh.get_branches() if x]
        except GithubException as error:
            log.warning(u"Unable to contact github, can't check for update: {0!r}", error)
            return []