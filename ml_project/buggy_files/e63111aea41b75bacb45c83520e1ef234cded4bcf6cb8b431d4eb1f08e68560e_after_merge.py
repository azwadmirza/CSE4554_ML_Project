    def write(self, path=None, tags=None):
        """Write the item's metadata to a media file.

        All fields in `_media_fields` are written to disk according to
        the values on this object.

        `path` is the path of the mediafile to wirte the data to. It
        defaults to the item's path.

        `tags` is a dictionary of additional metadata the should be
        written to the file. (These tags need not be in `_media_fields`.)

        Can raise either a `ReadError` or a `WriteError`.
        """
        if path is None:
            path = self.path
        else:
            path = normpath(path)

        # Get the data to write to the file.
        item_tags = dict(self)
        item_tags = {k: v for k, v in item_tags.items()
                     if k in self._media_fields}  # Only write media fields.
        if tags is not None:
            item_tags.update(tags)
        plugins.send('write', item=self, path=path, tags=item_tags)

        # Open the file.
        try:
            mediafile = MediaFile(syspath(path),
                                  id3v23=beets.config['id3v23'].get(bool))
        except (OSError, IOError, UnreadableFileError) as exc:
            raise ReadError(self.path, exc)

        # Write the tags to the file.
        mediafile.update(item_tags)
        try:
            mediafile.save()
        except (OSError, IOError, MutagenError) as exc:
            raise WriteError(self.path, exc)

        # The file has a new mtime.
        if path == self.path:
            self.mtime = self.current_mtime()
        plugins.send('after_write', item=self, path=path)