    def _eval_repo_url(repo_url):
        """Allow passing short GitHub style URLs"""
        if not repo_url:
            raise Exception('No valid repo_url provided or could be inferred.')
        if repo_url.startswith("file://"):
            return repo_url
        else:
            if len(repo_url.split('/')) == 2 and 'git@' not in repo_url:
                url = 'https://github.com/{}'.format(repo_url)
            else:
                url = repo_url
            return url if url.endswith('.git') else '{}.git'.format(url)