    def fx(self, func, *args, **kwargs):
        """

        Returns the result of ``func(self, *args, **kwargs)``.
        for instance

        >>> newclip = clip.fx(resize, 0.2, method="bilinear")

        is equivalent to

        >>> newclip = resize(clip, 0.2, method="bilinear")

        The motivation of fx is to keep the name of the effect near its
        parameters when the effects are chained:

        >>> from moviepy.video.fx import volumex, resize, mirrorx
        >>> clip.fx(volumex, 0.5).fx(resize, 0.3).fx(mirrorx)
        >>> # Is equivalent, but clearer than
        >>> mirrorx(resize(volumex(clip, 0.5), 0.3))
        """

        return func(self, *args, **kwargs)