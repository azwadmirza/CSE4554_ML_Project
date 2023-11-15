    def figimage(self, X,
                 xo=0,
                 yo=0,
                 alpha=None,
                 norm=None,
                 cmap=None,
                 vmin=None,
                 vmax=None,
                 origin=None,
                 **kwargs):
        """
        Adds a non-resampled image to the figure.

        call signatures::

          figimage(X, **kwargs)

        adds a non-resampled array *X* to the figure.

        ::

          figimage(X, xo, yo)

        with pixel offsets *xo*, *yo*,

        *X* must be a float array:

        * If *X* is MxN, assume luminance (grayscale)
        * If *X* is MxNx3, assume RGB
        * If *X* is MxNx4, assume RGBA

        Optional keyword arguments:

          =========   =========================================================
          Keyword     Description
          =========   =========================================================
          xo or yo    An integer, the *x* and *y* image offset in pixels
          cmap        a :class:`matplotlib.colors.Colormap` instance, eg
                      cm.jet. If *None*, default to the rc ``image.cmap``
                      value
          norm        a :class:`matplotlib.colors.Normalize` instance. The
                      default is normalization().  This scales luminance -> 0-1
          vmin|vmax   are used to scale a luminance image to 0-1.  If either
                      is *None*, the min and max of the luminance values will
                      be used.  Note if you pass a norm instance, the settings
                      for *vmin* and *vmax* will be ignored.
          alpha       the alpha blending value, default is *None*
          origin      [ 'upper' | 'lower' ] Indicates where the [0,0] index of
                      the array is in the upper left or lower left corner of
                      the axes. Defaults to the rc image.origin value
          =========   =========================================================

        figimage complements the axes image
        (:meth:`~matplotlib.axes.Axes.imshow`) which will be resampled
        to fit the current axes.  If you want a resampled image to
        fill the entire figure, you can define an
        :class:`~matplotlib.axes.Axes` with size [0,1,0,1].

        An :class:`matplotlib.image.FigureImage` instance is returned.

        .. plot:: mpl_examples/pylab_examples/figimage_demo.py


        Additional kwargs are Artist kwargs passed on to
        :class:`~matplotlib.image.FigureImage`
        """

        if not self._hold:
            self.clf()

        im = FigureImage(self, cmap, norm, xo, yo, origin, **kwargs)
        im.set_array(X)
        im.set_alpha(alpha)
        if norm is None:
            im.set_clim(vmin, vmax)
        self.images.append(im)
        return im