    def _compute_filename(self, obj, info, filename=None):
        if filename is None:
            hashfn = sha256()
            obj_str = 'None' if obj is None else self.object_formatter(obj)
            dimensions = self._dim_formatter(obj)
            dimensions = dimensions if dimensions else ''

            hashfn.update(obj_str.encode('utf-8'))
            label = sanitizer(getattr(obj, 'label', 'no-label'))
            group = sanitizer(getattr(obj, 'group', 'no-group'))
            format_values = {'timestamp': '{timestamp}',
                             'dimensions': dimensions,
                             'group':   group,
                             'label':   label,
                             'type':    obj.__class__.__name__,
                             'obj':     sanitizer(obj_str),
                             'SHA':     hashfn.hexdigest()}

            filename = self._format(self.filename_formatter,
                                    dict(info, **format_values))

        filename = self._normalize_name(filename)
        ext = info.get('file-ext', '')
        (unique_key, ext) = self._unique_name(filename, ext,
                                              self._files.keys(), force=True)
        return (unique_key, ext)