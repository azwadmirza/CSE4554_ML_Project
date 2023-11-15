    def annotations(self, issue, issue_obj):
        comments = self.jira.comments(issue.key) or []
        return self.build_annotations(
            ((
                comment.author.displayName,
                comment.body
            ) for comment in comments),
            issue_obj.get_processed_url(issue_obj.get_url())
        )