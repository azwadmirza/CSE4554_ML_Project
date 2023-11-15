    def __init__(self, filename, width=None, height=None,
                 kind='direct', mask="auto", lazy=1, client=None, target=None):
        # Client is mandatory.  Perhaps move it farther up if we refactor
        assert client is not None
        self.__kind=kind

        if filename.split("://")[0].lower() in ('http','ftp','https'):
            try:
                filename2, _ = urlretrieve(filename)
                if filename != filename2:
                    client.to_unlink.append(filename2)
                    filename = filename2
            except IOError:
                filename = missing
        self.filename, self._backend=self.get_backend(filename, client)
        srcinfo = client, self.filename

        if kind == 'percentage_of_container':
            self.image=self._backend(self.filename, width, height,
                'direct', mask, lazy, srcinfo)
            self.image.drawWidth=width
            self.image.drawHeight=height
            self.__width=width
            self.__height=height
        else:
            self.image=self._backend(self.filename, width, height,
                kind, mask, lazy, srcinfo)
        self.__ratio=float(self.image.imageWidth)/self.image.imageHeight
        self.__wrappedonce=False
        self.target = target