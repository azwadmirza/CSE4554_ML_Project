    def handle_repo_push(self, payload):
        changes = []
        project = payload['repository']['project']['name']
        repo_url = payload['repository']['links']['self']['href']
        web_url = payload['repository']['links']['html']['href']

        for payload_change in payload['push']['changes']:
            if payload_change['new']:
                age = 'new'
                category = 'push'
            else:  # when new is null the ref is deleted
                age = 'old'
                category = 'ref-deleted'

            commit_hash = payload_change[age]['target']['hash']

            if payload_change[age]['type'] == 'branch':
                branch = GIT_BRANCH_REF.format(payload_change[age]['name'])
            elif payload_change[age]['type'] == 'tag':
                branch = GIT_TAG_REF.format(payload_change[age]['name'])

            change = {
                'revision': commit_hash,
                'revlink': '{}/commits/{}'.format(web_url, commit_hash),
                'repository': repo_url,
                'author': '{} <{}>'.format(payload['actor']['display_name'],
                                           payload['actor']['username']),
                'comments': 'Bitbucket Cloud commit {}'.format(commit_hash),
                'branch': branch,
                'project': project,
                'category': category
            }

            if callable(self._codebase):
                change['codebase'] = self._codebase(payload)
            elif self._codebase is not None:
                change['codebase'] = self._codebase

            changes.append(change)

        return (changes, payload['repository']['scm'])