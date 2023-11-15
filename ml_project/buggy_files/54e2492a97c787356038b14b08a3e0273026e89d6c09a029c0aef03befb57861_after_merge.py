    def writerest(self, directory):
        """Write self.rest to a ReST file
        """
        if self.rest is not None and self.artist is not None:
            path = os.path.join(directory, 'artists',
                                slug(self.artist) + u'.rst')
            with open(path, 'wb') as output:
                output.write(self.rest.encode('utf-8'))