    def __call__(self, projectables, **info):
        if len(projectables) != 2:
            raise ValueError("Expected 2 datasets, got %d" %
                             (len(projectables), ))

        # TODO: support datasets with palette to delegate this to the image
        # writer.

        data, palette = projectables
        palette = np.asanyarray(palette).squeeze() / 255.0
        colormap = self.build_colormap(palette, data.dtype, data.attrs)

        channels, colors = colormap.palettize(np.asanyarray(data.squeeze()))
        channels = palette[channels]

        r = xr.DataArray(channels[:, :, 0].reshape(data.shape),
                         dims=data.dims, coords=data.coords)
        g = xr.DataArray(channels[:, :, 1].reshape(data.shape),
                         dims=data.dims, coords=data.coords)
        b = xr.DataArray(channels[:, :, 2].reshape(data.shape),
                         dims=data.dims, coords=data.coords)

        return super(PaletteCompositor, self).__call__((r, g, b), **data.attrs)