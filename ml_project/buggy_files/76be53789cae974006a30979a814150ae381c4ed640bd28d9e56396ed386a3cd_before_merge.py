    def get_image(self, tile):
        if six.PY3:
            from urllib.request import urlopen
        else:
            from urllib2 import urlopen

        url = self._image_url(tile)

        fh = urlopen(url)
        im_data = six.BytesIO(fh.read())
        fh.close()
        img = Image.open(im_data)

        img = img.convert(self.desired_tile_form)

        return img, self.tileextent(tile), 'lower'