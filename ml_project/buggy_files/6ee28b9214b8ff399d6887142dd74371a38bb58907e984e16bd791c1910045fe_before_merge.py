    def get_annotations(self, tag, issue, issue_obj, url):
        response = self.get_data(
            self.BASE_API +
            '/repositories/%s/issues/%i/comments' % (tag, issue['id']))
        return self.build_annotations(
            ((
                comment['author_info']['username'],
                comment['content'],
            ) for comment in response),
            issue_obj.get_processed_url(url)
        )