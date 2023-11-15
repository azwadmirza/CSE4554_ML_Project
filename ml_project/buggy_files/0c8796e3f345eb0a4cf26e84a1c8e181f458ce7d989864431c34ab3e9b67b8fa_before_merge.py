    def save(self_or_cls, obj, basename, fmt='auto', key={}, info={}, options=None, **kwargs):
        """
        Save a HoloViews object to file, either using an explicitly
        supplied format or to the appropriate default.
        """
        if info or key:
            raise Exception('MPLRenderer does not support saving metadata to file.')

        with StoreOptions.options(obj, options, **kwargs):
            plot = self_or_cls.get_plot(obj)

        if (fmt in list(self_or_cls.widgets.keys())+['auto']) and len(plot) > 1:
            with StoreOptions.options(obj, options, **kwargs):
                self_or_cls.export_widgets(plot, basename+'.html', fmt)
            return

        with StoreOptions.options(obj, options, **kwargs):
            rendered = self_or_cls(plot, fmt)
        if rendered is None: return
        (data, info) = rendered
        if isinstance(basename, BytesIO):
            basename.write(data)
            basename.seek(0)
        else:
            encoded = self_or_cls.encode(rendered)
            filename ='%s.%s' % (basename, info['file-ext'])
            with open(filename, 'wb') as f:
                f.write(encoded)