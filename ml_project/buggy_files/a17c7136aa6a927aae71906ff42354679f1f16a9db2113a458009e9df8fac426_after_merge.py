    def update_repo(self, name):

        def run(*args, **kwargs):
            env = os.environ.copy()
            env['GIT_TERMINAL_PROMPT'] = '0'
            kwargs['env'] = env
            return sp_run(*args, **kwargs)

        try:
            dd = self.path
            if name not in self.repos:
                raise UpdateError("Repo does not exist in data, wtf")
            folder = os.path.join(dd, name)
            # Make sure we don't git reset the Red folder on accident
            if not os.path.exists(os.path.join(folder, '.git')):
                #if os.path.exists(folder):
                    #shutil.rmtree(folder)
                url = self.repos[name].get('url')
                if not url:
                    raise UpdateError("Need to clone but no URL set")
                branch = None
                if "@" in url: # Specific branch
                    url, branch = url.rsplit("@", maxsplit=1)
                if branch is None:
                    p = run(["git", "clone", url, dd + name])
                else:
                    p = run(["git", "clone", "-b", branch, url, dd + name])
                if p.returncode != 0:
                    raise CloningError()
                self.populate_list(name)
                return name, REPO_CLONE, None
            else:
                rpcmd = ["git", "-C", dd + name, "rev-parse", "HEAD"]
                p = run(["git", "-C", dd + name, "reset", "--hard",
                        "origin/HEAD", "-q"])
                if p.returncode != 0:
                    raise UpdateError("Error resetting to origin/HEAD")
                p = run(rpcmd, stdout=PIPE)
                if p.returncode != 0:
                    raise UpdateError("Unable to determine old commit hash")
                oldhash = p.stdout.decode().strip()
                p = run(["git", "-C", dd + name, "pull", "-q", "--ff-only"])
                if p.returncode != 0:
                    raise UpdateError("Error pulling updates")
                p = run(rpcmd, stdout=PIPE)
                if p.returncode != 0:
                    raise UpdateError("Unable to determine new commit hash")
                newhash = p.stdout.decode().strip()
                if oldhash == newhash:
                    return name, REPO_SAME, None
                else:
                    self.populate_list(name)
                    self.save_repos()
                    ret = {}
                    cmd = ['git', '-C', dd + name, 'diff', '--no-commit-id',
                           '--name-status', oldhash, newhash]
                    p = run(cmd, stdout=PIPE)

                    if p.returncode != 0:
                        raise UpdateError("Error in git diff")

                    changed = p.stdout.strip().decode().split('\n')

                    for f in changed:
                        if not f.endswith('.py'):
                            continue

                        status, _, cogpath = f.partition('\t')
                        cogname = os.path.split(cogpath)[-1][:-3]  # strip .py
                        if status not in ret:
                            ret[status] = []
                        ret[status].append(cogname)

                    return name, ret, oldhash

        except CloningError as e:
            raise CloningError(name, *e.args) from None
        except UpdateError as e:
            raise UpdateError(name, *e.args) from None