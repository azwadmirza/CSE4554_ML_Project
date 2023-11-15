    def check_github(self):
        """
        If the requirement is frozen to a github url, check for new commits.

        API Tokens
        ----------
        For more than 50 github api calls per hour, pipchecker requires
        authentication with the github api by settings the environemnt
        variable ``GITHUB_API_TOKEN`` or setting the command flag
        --github-api-token='mytoken'``.

        To create a github api token for use at the command line::
             curl -u 'rizumu' -d '{"scopes":["repo"], "note":"pipchecker"}' https://api.github.com/authorizations

        For more info on github api tokens:
            https://help.github.com/articles/creating-an-oauth-token-for-command-line-use
            http://developer.github.com/v3/oauth/#oauth-authorizations-api

        Requirement Format
        ------------------
        Pipchecker gets the sha of frozen repo and checks if it is
        found at the head of any branches. If it is not found then
        the requirement is considered to be out of date.

        Therefore, freezing at the commit hash will provide the expected
        results, but if freezing at a branch or tag name, pipchecker will
        not be able to determine with certainty if the repo is out of date.

        Freeze at the commit hash (sha)::
            git+git://github.com/django/django.git@393c268e725f5b229ecb554f3fac02cfc250d2df#egg=Django
            https://github.com/django/django/archive/393c268e725f5b229ecb554f3fac02cfc250d2df.tar.gz#egg=Django
            https://github.com/django/django/archive/393c268e725f5b229ecb554f3fac02cfc250d2df.zip#egg=Django

        Freeze with a branch name::
            git+git://github.com/django/django.git@master#egg=Django
            https://github.com/django/django/archive/master.tar.gz#egg=Django
            https://github.com/django/django/archive/master.zip#egg=Django

        Freeze with a tag::
            git+git://github.com/django/django.git@1.5b2#egg=Django
            https://github.com/django/django/archive/1.5b2.tar.gz#egg=Django
            https://github.com/django/django/archive/1.5b2.zip#egg=Django

        Do not freeze::
            git+git://github.com/django/django.git#egg=Django

        """
        for name, req in list(self.reqs.items()):
            req_url = req["url"]
            if not req_url:
                continue
            req_url = str(req_url)
            if req_url.startswith("git") and "github.com/" not in req_url:
                continue
            if req_url.endswith((".tar.gz", ".tar.bz2", ".zip")):
                continue

            headers = {
                "content-type": "application/json",
            }
            if self.github_api_token:
                headers["Authorization"] = "token {0}".format(self.github_api_token)
            try:
                path_parts = urlparse(req_url).path.split("#", 1)[0].strip("/").rstrip("/").split("/")

                if len(path_parts) == 2:
                    user, repo = path_parts

                elif 'archive' in path_parts:
                    # Supports URL of format:
                    # https://github.com/django/django/archive/master.tar.gz#egg=Django
                    # https://github.com/django/django/archive/master.zip#egg=Django
                    user, repo = path_parts[:2]
                    repo += '@' + path_parts[-1].replace('.tar.gz', '').replace('.zip', '')

                else:
                    self.style.ERROR("\nFailed to parse %r\n" % (req_url, ))
                    continue
            except (ValueError, IndexError) as e:
                self.stdout.write(self.style.ERROR("\nFailed to parse %r: %s\n" % (req_url, e)))
                continue

            try:
                test_auth = requests.get("https://api.github.com/django/", headers=headers).json()
            except HTTPError as e:
                self.stdout.write("\n%s\n" % str(e))
                return

            if "message" in test_auth and test_auth["message"] == "Bad credentials":
                self.stdout.write(self.style.ERROR("\nGithub API: Bad credentials. Aborting!\n"))
                return
            elif "message" in test_auth and test_auth["message"].startswith("API Rate Limit Exceeded"):
                self.stdout.write(self.style.ERROR("\nGithub API: Rate Limit Exceeded. Aborting!\n"))
                return

            frozen_commit_sha = None
            if ".git" in repo:
                repo_name, frozen_commit_full = repo.split(".git")
                if frozen_commit_full.startswith("@"):
                    frozen_commit_sha = frozen_commit_full[1:]
            elif "@" in repo:
                repo_name, frozen_commit_sha = repo.split("@")

            if frozen_commit_sha is None:
                msg = self.style.ERROR("repo is not frozen")

            if frozen_commit_sha:
                branch_url = "https://api.github.com/repos/{0}/{1}/branches".format(user, repo_name)
                branch_data = requests.get(branch_url, headers=headers).json()

                frozen_commit_url = "https://api.github.com/repos/{0}/{1}/commits/{2}".format(
                    user, repo_name, frozen_commit_sha
                )
                frozen_commit_data = requests.get(frozen_commit_url, headers=headers).json()

                if "message" in frozen_commit_data and frozen_commit_data["message"] == "Not Found":
                    msg = self.style.ERROR("{0} not found in {1}. Repo may be private.".format(frozen_commit_sha[:10], name))
                elif frozen_commit_data["sha"] in [branch["commit"]["sha"] for branch in branch_data]:
                    msg = self.style.BOLD("up to date")
                else:
                    msg = self.style.INFO("{0} is not the head of any branch".format(frozen_commit_data["sha"][:10]))

            if "dist" in req:
                pkg_info = "{dist.project_name} {dist.version}".format(dist=req["dist"])
            elif frozen_commit_sha is None:
                pkg_info = name
            else:
                pkg_info = "{0} {1}".format(name, frozen_commit_sha[:10])
            self.stdout.write("{pkg_info:40} {msg}".format(pkg_info=pkg_info, msg=msg))
            del self.reqs[name]