    def is_forked(self, owner, repo): #/repos/:owner/:repo parent
        logging.info('Querying parent info to verify if the repo is forked\n')
        url = f'https://api.github.com/repos/{owner}/{repo}'

        r = requests.get(url, headers=self.headers)
        self.update_gh_rate_limit(r)

        data = self.get_repo_data(url, r)

        if 'fork' in data:
            if 'parent' in data:
                return data['parent']['full_name']
            return 'Parent not available'

        return False