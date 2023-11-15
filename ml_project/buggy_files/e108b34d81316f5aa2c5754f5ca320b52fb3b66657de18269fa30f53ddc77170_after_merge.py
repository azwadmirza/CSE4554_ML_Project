    def resize_image(self, src, dst, max_size, bigger_panoramas=True):
        """Make a copy of the image in the requested size."""
        if not Image or os.path.splitext(src)[1] in ['.svg', '.svgz']:
            utils.copy_file(src, dst)
            return
        im = Image.open(src)
        w, h = im.size
        if w > max_size or h > max_size:
            size = max_size, max_size

            # Panoramas get larger thumbnails because they look *awful*
            if bigger_panoramas and w > 2 * h:
                size = min(w, max_size * 4), min(w, max_size * 4)

            try:
                exif = im._getexif()
            except Exception:
                exif = None
            if exif is not None:
                for tag, value in list(exif.items()):
                    decoded = ExifTags.TAGS.get(tag, tag)

                    if decoded == 'Orientation':
                        if value == 3:
                            im = im.rotate(180)
                        elif value == 6:
                            im = im.rotate(270)
                        elif value == 8:
                            im = im.rotate(90)
                        break
            try:
                im.thumbnail(size, Image.ANTIALIAS)
                im.save(dst)
            except Exception as e:
                self.logger.warn("Can't thumbnail {0}, using original "
                                 "image as thumbnail ({1})".format(src, e))
                utils.copy_file(src, dst)
        else:  # Image is small
            utils.copy_file(src, dst)