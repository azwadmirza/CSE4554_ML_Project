    def comment(self, data):
        self.start(XmlET.Comment, {})
        self.data(data)
        self.end(XmlET.Comment)