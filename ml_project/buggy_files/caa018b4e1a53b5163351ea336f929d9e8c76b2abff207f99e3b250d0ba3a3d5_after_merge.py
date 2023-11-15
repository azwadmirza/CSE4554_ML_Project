    def comment(self, data):
        if self.non_comment_seen:
            # Cannot start XML file with comment
            self.start(XmlET.Comment, {})
            self.data(data)
            self.end(XmlET.Comment)