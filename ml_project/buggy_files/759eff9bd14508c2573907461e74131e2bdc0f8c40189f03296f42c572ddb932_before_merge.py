    def list_remote_branches():
        gh = get_github_repo(app.GIT_ORG, app.GIT_REPO)
        return [x.name for x in gh.get_branches() if x]