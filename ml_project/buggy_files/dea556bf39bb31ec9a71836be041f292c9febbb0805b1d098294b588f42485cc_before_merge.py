    def issues(self):
        user = self.config.get('username')
        response = self.get_collection('/repositories/' + user + '/')
        repo_tags = list(filter(self.filter_repos, [
            repo['full_name'] for repo in response
            if repo.get('has_issues')
        ]))

        issues = sum([self.fetch_issues(repo) for repo in repo_tags], [])
        log.debug(" Found %i total.", len(issues))

        closed = ['resolved', 'duplicate', 'wontfix', 'invalid', 'closed']
        try:
            issues = [tup for tup in issues if tup[1]['status'] not in closed]
        except KeyError:  # Undocumented API change.
            issues = [tup for tup in issues if tup[1]['state'] not in closed]
        issues = list(filter(self.include, issues))
        log.debug(" Pruned down to %i", len(issues))

        for tag, issue in issues:
            issue_obj = self.get_issue_for_record(issue)
            tagParts = tag.split('/')
            projectName = tagParts[1]
            if self.project_owner_prefix:
                projectName = tagParts[0] + "." + projectName
            url = issue['links']['html']['href']
            extras = {
                'project': projectName,
                'url': url,
                'annotations': self.get_annotations(tag, issue, issue_obj, url)
            }
            issue_obj.update_extra(extras)
            yield issue_obj

        if not self.filter_merge_requests:
            pull_requests = sum(
                [self.fetch_pull_requests(repo) for repo in repo_tags], [])
            log.debug(" Found %i total.", len(pull_requests))

            closed = ['rejected', 'fulfilled']
            not_resolved = lambda tup: tup[1]['state'] not in closed
            pull_requests = list(filter(not_resolved, pull_requests))
            pull_requests = list(filter(self.include, pull_requests))
            log.debug(" Pruned down to %i", len(pull_requests))

            for tag, issue in pull_requests:
                issue_obj = self.get_issue_for_record(issue)
                tagParts = tag.split('/')
                projectName = tagParts[1]
                if self.project_owner_prefix:
                    projectName = tagParts[0] + "." + projectName
                url = self.BASE_URL + '/'.join(
                    issue['links']['html']['href'].split('/')[3:]
                ).replace('pullrequests', 'pullrequest')
                extras = {
                    'project': projectName,
                    'url': url,
                    'annotations': self.get_annotations2(tag, issue, issue_obj, url)
                }
                issue_obj.update_extra(extras)
                yield issue_obj