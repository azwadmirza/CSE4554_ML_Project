    def _axes_domain(self, nx=None, ny=None, background_patch=None):
        """Returns x_range, y_range"""
        DEBUG = False

        transform = self._crs_transform()

        ax_transform = self.axes.transAxes
        desired_trans = ax_transform - transform

        nx = nx or 30
        ny = ny or 30
        x = np.linspace(1e-9, 1 - 1e-9, nx)
        y = np.linspace(1e-9, 1 - 1e-9, ny)
        x, y = np.meshgrid(x, y)

        coords = np.concatenate([x.flatten()[:, None],
                                 y.flatten()[:, None]],
                                1)

        in_data = desired_trans.transform(coords)

        ax_to_bkg_patch = self.axes.transAxes - \
            background_patch.get_transform()

        ok = np.zeros(in_data.shape[:-1], dtype=np.bool)
        # XXX Vectorise contains_point
        for i, val in enumerate(in_data):
            # convert the coordinates of the data to the background
            # patches coordinates
            background_coord = ax_to_bkg_patch.transform(coords[i:i + 1, :])
            bkg_patch_contains = background_patch.get_path().contains_point
            if bkg_patch_contains(background_coord[0, :]):
                color = 'r'
                ok[i] = True
            else:
                color = 'b'

            if DEBUG:
                import matplotlib.pyplot as plt
                plt.plot(coords[i, 0], coords[i, 1], 'o' + color,
                         clip_on=False, transform=ax_transform)
#                plt.text(coords[i, 0], coords[i, 1], str(val), clip_on=False,
#                         transform=ax_transform, rotation=23,
#                         horizontalalignment='right')

        inside = in_data[ok, :]

        # If there were no data points in the axes we just use the x and y
        # range of the projection.
        if inside.size == 0:
            x_range = self.crs.x_limits
            y_range = self.crs.y_limits
        else:
            x_range = np.nanmin(inside[:, 0]), np.nanmax(inside[:, 0])
            y_range = np.nanmin(inside[:, 1]), np.nanmax(inside[:, 1])

        # XXX Cartopy specific thing. Perhaps make this bit a specialisation
        # in a subclass...
        crs = self.crs
        if isinstance(crs, Projection):
            x_range = np.clip(x_range, *crs.x_limits)
            y_range = np.clip(y_range, *crs.y_limits)

            # if the limit is >90% of the full x limit, then just use the full
            # x limit (this makes circular handling better)
            prct = np.abs(np.diff(x_range) / np.diff(crs.x_limits))
            if prct > 0.9:
                x_range = crs.x_limits

        return x_range, y_range