    def __call__(self, projectables, **info):
        if len(projectables) != 2:
            raise ValueError("Expected 2 datasets, got %d" %
                             (len(projectables), ))

        # TODO: support datasets with palette to delegate this to the image
        # writer.

        data, palette = projectables
        palette = np.asanyarray(palette).squeeze()
        colormap = self.build_colormap(palette / 255.0, data.dtype, data.attrs)

        r, g, b = colormap.colorize(np.asanyarray(data))
        r[data.mask] = palette[-1][0]
        g[data.mask] = palette[-1][1]
        b[data.mask] = palette[-1][2]
        r = Dataset(r, copy=False, mask=data.mask, **data.attrs)
        g = Dataset(g, copy=False, mask=data.mask, **data.attrs)
        b = Dataset(b, copy=False, mask=data.mask, **data.attrs)

        return super(ColorizeCompositor, self).__call__((r, g, b), **data.attrs)