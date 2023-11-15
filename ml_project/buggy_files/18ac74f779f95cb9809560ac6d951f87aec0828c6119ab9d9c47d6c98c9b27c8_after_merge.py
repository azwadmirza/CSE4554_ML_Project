        def _dup(lib, opts, args):
            self.config.set_args(opts)
            album = self.config['album'].get(bool)
            checksum = self.config['checksum'].get(str)
            copy = self.config['copy'].get(str)
            count = self.config['count'].get(bool)
            delete = self.config['delete'].get(bool)
            fmt = self.config['format'].get(str)
            full = self.config['full'].get(bool)
            keys = self.config['keys'].get(list)
            move = self.config['move'].get(str)
            path = self.config['path'].get(bool)
            strict = self.config['strict'].get(bool)
            tag = self.config['tag'].get(str)

            if album:
                keys = ['mb_albumid']
                items = lib.albums(decargs(args))
            else:
                items = lib.items(decargs(args))

            if path:
                fmt = '$path'

            # Default format string for count mode.
            if count and not fmt:
                if album:
                    fmt = '$albumartist - $album'
                else:
                    fmt = '$albumartist - $album - $title'
                fmt += ': {0}'

            if checksum:
                for i in items:
                    k, _ = self._checksum(i, checksum)
                keys = [k]

            for obj_id, obj_count, objs in self._duplicates(items,
                                                            keys=keys,
                                                            full=full,
                                                            strict=strict):
                if obj_id:  # Skip empty IDs.
                    for o in objs:
                        self._process_item(o, lib,
                                           copy=copy,
                                           move=move,
                                           delete=delete,
                                           tag=tag,
                                           fmt=fmt.format(obj_count))