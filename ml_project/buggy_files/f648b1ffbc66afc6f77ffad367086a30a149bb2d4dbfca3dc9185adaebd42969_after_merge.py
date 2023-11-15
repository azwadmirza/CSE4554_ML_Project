    def is_archived(self, owner, repo):
        self.logger.info('Querying committers count\n')
        url = f'https://api.github.com/repos/{owner}/{repo}'

        r = requests.get(url, headers=self.headers)
        self.update_gh_rate_limit(r)

        data = self.get_repo_data(url, r)

        if 'archived' in data:
            if data['archived']:
                if 'updated_at' in data:
                    return data['updated_at']
                return 'Date not available'
            return False

        return False