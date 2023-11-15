        def updatefig(i, im, annotate, ani_data, removes):
            while removes:
                removes.pop(0).remove()

            im.set_array(ani_data[i].data)
            im.set_cmap(ani_data[i].plot_settings['cmap'])

            norm = deepcopy(ani_data[i].plot_settings['norm'])
            # The following explicit call is for bugged versions of Astropy's
            # ImageNormalize
            norm.autoscale_None(ani_data[i].data)
            im.set_norm(norm)

            if wcsaxes_compat.is_wcsaxes(axes):
                im.axes.reset_wcs(ani_data[i].wcs)
                wcsaxes_compat.default_wcs_grid(axes)
            else:
                im.set_extent(np.concatenate((ani_data[i].xrange.value,
                                              ani_data[i].yrange.value)))

            if annotate:
                annotate_frame(i)
            removes += list(plot_function(fig, axes, ani_data[i]))