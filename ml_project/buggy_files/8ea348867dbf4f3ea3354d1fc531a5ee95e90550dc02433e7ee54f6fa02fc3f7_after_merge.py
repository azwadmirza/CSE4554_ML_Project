    def patch_notes_handler(self, repo_cog_hash_pairs):
        for repo, cog, oldhash in repo_cog_hash_pairs:
            pathsplit = self.repos[repo][cog]['file'].split('/')
            repo_path = os.path.join(*pathsplit[:-2])
            cogfile = os.path.join(*pathsplit[-2:])
            cmd = ["git", "-C", repo_path, "log", "--relative-date",
                   "--reverse", oldhash + '..', cogfile
                   ]
            try:
                log = sp_run(cmd, stdout=PIPE).stdout.decode().strip()
                yield self.format_patch(repo, cog, log)
            except:
                pass