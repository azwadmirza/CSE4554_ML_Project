    def __call__(self, obj, fmt='auto'):
        """
        Render the supplied HoloViews component or MPLPlot instance
        using matplotlib.
        """
        plot, fmt =  self._validate(obj, fmt)
        if plot is None: return

        if isinstance(plot, tuple(self.widgets.values())):
            data = plot()
        elif fmt in ['png', 'svg', 'pdf', 'html', 'json']:
            data = self._figure_data(plot, fmt, **({'dpi':self.dpi} if self.dpi else {}))
        else:
            if sys.version_info[0] == 3 and mpl.__version__[:-2] in ['1.2', '1.3']:
                raise Exception("<b>Python 3 matplotlib animation support broken &lt;= 1.3</b>")
            anim = plot.anim(fps=self.fps)
            data = self._anim_data(anim, fmt)

        data = self._apply_post_render_hooks(data, obj, fmt)
        return data, {'file-ext':fmt,
                      'mime_type':MIME_TYPES[fmt]}