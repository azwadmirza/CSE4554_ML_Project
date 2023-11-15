    def convert_item(self, dest_dir, keep_new, path_formats, fmt,
                     pretend=False):
        command, ext = get_format(fmt)
        item, original, converted = None, None, None
        while True:
            item = yield (item, original, converted)
            dest = item.destination(basedir=dest_dir,
                                    path_formats=path_formats)

            # When keeping the new file in the library, we first move the
            # current (pristine) file to the destination. We'll then copy it
            # back to its old path or transcode it to a new path.
            if keep_new:
                original = dest
                converted = item.path
                if should_transcode(item, fmt):
                    converted = replace_ext(converted, ext)
            else:
                original = item.path
                if should_transcode(item, fmt):
                    dest = replace_ext(dest, ext)
                converted = dest

            # Ensure that only one thread tries to create directories at a
            # time. (The existence check is not atomic with the directory
            # creation inside this function.)
            if not pretend:
                with _fs_lock:
                    util.mkdirall(dest)

            if os.path.exists(util.syspath(dest)):
                self._log.info(u'Skipping {0} (target file exists)',
                               util.displayable_path(item.path))
                continue

            if keep_new:
                if pretend:
                    self._log.info(u'mv {0} {1}',
                                   util.displayable_path(item.path),
                                   util.displayable_path(original))
                else:
                    self._log.info(u'Moving to {0}',
                                   util.displayable_path(original))
                    util.move(item.path, original)

            if should_transcode(item, fmt):
                try:
                    self.encode(command, original, converted, pretend)
                except subprocess.CalledProcessError:
                    continue
            else:
                if pretend:
                    self._log.info(u'cp {0} {1}',
                                   util.displayable_path(original),
                                   util.displayable_path(converted))
                else:
                    # No transcoding necessary.
                    self._log.info(u'Copying {0}',
                                   util.displayable_path(item.path))
                    util.copy(original, converted)

            if pretend:
                continue

            # Write tags from the database to the converted file.
            item.try_write(path=converted)

            if keep_new:
                # If we're keeping the transcoded file, read it again (after
                # writing) to get new bitrate, duration, etc.
                item.path = converted
                item.read()
                item.store()  # Store new path and audio data.

            if self.config['embed']:
                album = item.get_album()
                if album and album.artpath:
                    EmbedCoverArtPlugin().embed_item(item, album.artpath,
                                                     itempath=converted)

            if keep_new:
                plugins.send('after_convert', item=item,
                             dest=dest, keepnew=True)
            else:
                plugins.send('after_convert', item=item,
                             dest=converted, keepnew=False)