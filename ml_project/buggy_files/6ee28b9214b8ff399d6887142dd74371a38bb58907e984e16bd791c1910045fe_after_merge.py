    def get_annotations(self, tag, issue, issue_obj, url):
        response = self.get_collection(
            '/repositories/%s/pullrequests/%i/comments' % (tag, issue['id'])
        )
        return self.build_annotations(
            ((
                comment['user']['username'],
                comment['content']['raw'],
            ) for comment in response),
            issue_obj.get_processed_url(url)
        )