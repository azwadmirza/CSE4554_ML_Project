    def save(self, targetdir, filename, meta_formats=None):
        """
        Store the image data into the target directory path,
        with given filename="dir/out.png"
        If metaformats are requested, export e.g. as "dir/out.docx".
        """
        if not isinstance(targetdir, Path):
            raise ValueError("util.fslike Path expected as targetdir")
        if not isinstance(filename, str):
            raise ValueError("str expected as filename, not %s" % type(filename))

        basename, ext = os.path.splitext(filename)

        # only allow png, although PIL could of course
        # do other formats.
        if ext != ".png":
            raise ValueError("Filename invalid, a texture must be saved"
                             "as 'filename.png', not '%s'" % (filename))

        # without the dot
        ext = ext[1:]

        # generate PNG file
        with targetdir[filename].open("wb") as imagefile:
            self.image_data.get_pil_image().save(imagefile, ext)

        if meta_formats:
            # generate formatted texture metadata
            formatter = data_formatter.DataFormatter()
            formatter.add_data(self.dump(basename))
            formatter.export(targetdir, meta_formats)