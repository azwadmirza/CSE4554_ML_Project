    def writerest(self, directory, item):
        """Write the item to an ReST file

        This will keep state (in the `rest` variable) in order to avoid
        writing continuously to the same files.
        """

        if item is None or slug(self.artist) != slug(item.albumartist):
            if self.rest is not None:
                path = os.path.join(directory, 'artists',
                                    slug(self.artist) + u'.rst')
                with open(path, 'wb') as output:
                    output.write(self.rest.encode('utf-8'))
                self.rest = None
                if item is None:
                    return
            self.artist = item.albumartist.strip()
            self.rest = u"%s\n%s\n\n.. contents::\n   :local:\n\n" \
                        % (self.artist,
                           u'=' * len(self.artist))
        if self.album != item.album:
            tmpalbum = self.album = item.album.strip()
            if self.album == '':
                tmpalbum = u'Unknown album'
            self.rest += u"%s\n%s\n\n" % (tmpalbum, u'-' * len(tmpalbum))
        title_str = u":index:`%s`" % item.title.strip()
        block = u'| ' + item.lyrics.replace(u'\n', u'\n| ')
        self.rest += u"%s\n%s\n\n%s\n\n" % (title_str,
                                            u'~' * len(title_str),
                                            block)