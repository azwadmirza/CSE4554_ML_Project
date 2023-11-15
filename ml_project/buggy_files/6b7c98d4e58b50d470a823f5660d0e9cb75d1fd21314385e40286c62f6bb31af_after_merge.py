    def query_committers_count(self, owner, repo):
        self.logger.info('Querying committers count\n')
        url = f'https://api.github.com/repos/{owner}/{repo}/contributors?per_page=100'
        committers = 0

        try:
            while True:
                r = requests.get(url, headers=self.headers)
                self.update_gh_rate_limit(r)
                committers += len(r.json())

                if 'next' not in r.links:
                    break
                else:
                    url = r.links['next']['url']
        except Exception:
            self.logger.exception('An error occured while querying contributor count\n')

        return committers