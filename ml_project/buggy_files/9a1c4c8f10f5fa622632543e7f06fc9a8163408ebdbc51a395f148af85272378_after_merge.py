    def handle_pullrequest(self, payload, refname, category):
        pr_number = int(payload['pullrequest']['id'])
        repo_url = payload['repository']['links']['self']['href']
        project = payload['repository'].get('project', {'name': 'none'})['name']
        change = {
            'revision': payload['pullrequest']['fromRef']['commit']['hash'],
            'revlink': payload['pullrequest']['link'],
            'repository': repo_url,
            'author': '{} <{}>'.format(payload['actor']['display_name'],
                                       payload['actor']['nickname']),
            'comments': 'Bitbucket Cloud Pull Request #{}'.format(pr_number),
            'branch': refname,
            'project': project,
            'category': category,
            'properties': {'pullrequesturl': payload['pullrequest']['link']}
        }

        if callable(self._codebase):
            change['codebase'] = self._codebase(payload)
        elif self._codebase is not None:
            change['codebase'] = self._codebase

        return [change], payload['repository']['scm']