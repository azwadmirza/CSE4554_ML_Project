        def scrub_func(lib, opts, args):
            # This is a little bit hacky, but we set a global flag to
            # avoid autoscrubbing when we're also explicitly scrubbing.
            global scrubbing
            scrubbing = True

            # Walk through matching files and remove tags.
            for item in lib.items(ui.decargs(args)):
                self._log.info(u'scrubbing: {0}',
                               util.displayable_path(item.path))

                # Get album art if we need to restore it.
                if opts.write:
                    mf = mediafile.MediaFile(item.path,
                                             config['id3v23'].get(bool))
                    art = mf.art

                # Remove all tags.
                self._scrub(item.path)

                # Restore tags, if enabled.
                if opts.write:
                    self._log.debug(u'writing new tags after scrub')
                    item.try_write()
                    if art:
                        self._log.info(u'restoring art')
                        mf = mediafile.MediaFile(item.path)
                        mf.art = art
                        mf.save()

            scrubbing = False