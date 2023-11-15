    def __call__(self, projectables, **info):
        if len(projectables) != 2:
            raise ValueError("Expected 2 datasets, got %d" %
                             (len(projectables), ))

        # TODO: support datasets with palette to delegate this to the image
        # writer.

        data, palette = projectables
        palette = palette / 255.0
        colormap = self.build_colormap(palette, data.dtype, data.info)

        channels, colors = colormap.palettize(data)
        channels = palette[channels]

        r = Dataset(channels[:, :, 0], copy=False, mask=data.mask, **data.info)
        g = Dataset(channels[:, :, 1], copy=False, mask=data.mask, **data.info)
        b = Dataset(channels[:, :, 2], copy=False, mask=data.mask, **data.info)

        return super(PaletteCompositor, self).__call__((r, g, b), **data.info)