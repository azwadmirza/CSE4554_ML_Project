    def _repr_html_(self):
        if not six.PY2:
            from html import escape
        else:
            from cgi import escape
        try:
            # As matplotlib is not a core cartopy dependency, don't error
            # if it's not available.
            import matplotlib.pyplot as plt
        except ImportError:
            # We can't return an SVG of the CRS, so let Jupyter fall back to
            # a default repr by returning None.
            return None

        # Produce a visual repr of the Projection instance.
        fig, ax = plt.subplots(figsize=(5, 3),
                               subplot_kw={'projection': self})
        ax.set_global()
        ax.coastlines('auto')
        ax.gridlines()
        buf = six.StringIO()
        fig.savefig(buf, format='svg', bbox_inches='tight')
        plt.close(fig)
        # "Rewind" the buffer to the start and return it as an svg string.
        buf.seek(0)
        svg = buf.read()
        return '{}<pre>{}</pre>'.format(svg, escape(repr(self)))