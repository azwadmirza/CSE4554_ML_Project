    def build_colormap(palette, dtype, info):
        """Create the colormap from the `raw_palette` and the valid_range."""

        from trollimage.colormap import Colormap

        palette = np.asanyarray(palette).squeeze()
        if dtype == np.dtype('uint8'):
            tups = [(val, tuple(tup))
                    for (val, tup) in enumerate(palette[:-1])]
            colormap = Colormap(*tups)

        elif 'valid_range' in info:
            tups = [(val, tuple(tup))
                    for (val, tup) in enumerate(palette[:-1])]
            colormap = Colormap(*tups)

            sf = info['scale_factor']
            colormap.set_range(
                *info['valid_range'] * sf + info['add_offset'])

        return colormap