    def get_image(self, tile):
        if six.PY3:
            from urllib.request import urlopen, Request, HTTPError, URLError
        else:
            from urllib2 import urlopen, Request, HTTPError, URLError

        url = self._image_url(tile)
        try:
            request = Request(url, headers={"user-agent": self.user_agent})
            fh = urlopen(request)
            im_data = six.BytesIO(fh.read())
            fh.close()
            img = Image.open(im_data)

        except (HTTPError, URLError) as err:
            print(err)
            img = Image.fromarray(np.full((256, 256, 3), (250, 250, 250),
                                          dtype=np.uint8))

        img = img.convert(self.desired_tile_form)
        return img, self.tileextent(tile), 'lower'