    def _write_image(self, image_data, image_path, obj=None):
        """
        Saves the data in image_data to the location image_path. Returns True/False
        to represent success or failure.

        image_data: binary image data to write to file
        image_path: file location to save the image to
        """

        assert isinstance(image_path, text_type)

        # don't bother overwriting it
        if ek(os.path.isfile, image_path):
            logger.log(u"Image already exists, not downloading", logger.DEBUG)
            return False

        image_dir = ek(os.path.dirname, image_path)

        if not image_data:
            logger.log(u"Unable to retrieve image to save in %s, skipping" % image_path, logger.DEBUG)
            return False

        try:
            if not ek(os.path.isdir, image_dir):
                logger.log(u"Metadata dir didn't exist, creating it at " + image_dir, logger.DEBUG)
                ek(os.makedirs, image_dir)
                helpers.chmodAsParent(image_dir)

            outFile = io.open(image_path, 'wb', encoding='utf8')
            outFile.write(image_data)
            outFile.close()
            helpers.chmodAsParent(image_path)
        except IOError as e:
            if hasattr(e, 'errno') and e.errno in (13, 28):  # Permission denied and No space left on device
                msg_level = logger.WARNING
            else:
                msg_level = logger.ERROR
            logger.log(u'Unable to write image to {0}. Error: {1}'.format
                       (image_path, e), msg_level)
            return False

        return True