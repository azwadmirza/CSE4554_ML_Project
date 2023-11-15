    def html(self, obj, fmt=None, css=None, comm=True, **kwargs):
        """
        Renders plot or data structure and wraps the output in HTML.
        The comm argument defines whether the HTML output includes
        code to initialize a Comm, if the plot supplies one.
        """
        plot, fmt =  self._validate(obj, fmt)
        figdata, _ = self(plot, fmt, **kwargs)
        if css is None: css = self.css

        if fmt in ['html', 'json']:
            return figdata
        else:
            if fmt == 'svg':
                figdata = figdata.encode("utf-8")
            elif fmt == 'pdf' and 'height' not in css:
                _, h = self.get_size(plot)
                css['height'] = '%dpx' % (h*self.dpi*1.15)

        if isinstance(css, dict):
            css = '; '.join("%s: %s" % (k, v) for k, v in css.items())
        else:
            raise ValueError("CSS must be supplied as Python dictionary")

        b64 = base64.b64encode(figdata).decode("utf-8")
        (mime_type, tag) = MIME_TYPES[fmt], HTML_TAGS[fmt]
        src = HTML_TAGS['base64'].format(mime_type=mime_type, b64=b64)
        html = tag.format(src=src, mime_type=mime_type, css=css)
        if comm and plot.comm is not None:
            comm, msg_handler = self.comms[self.mode]
            if msg_handler is None:
                return html
            msg_handler = msg_handler.format(comm_id=plot.comm.id)
            return comm.template.format(init_frame=html,
                                        msg_handler=msg_handler,
                                        comm_id=plot.comm.id)
        else:
            return html