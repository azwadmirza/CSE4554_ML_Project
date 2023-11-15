    def __call__(self, projectables, *args, **kwargs):
        """Create the SAR Ice composite."""
        (mhh, mhv) = projectables
        green = overlay(mhh, mhv)
        green.info = combine_info(mhh, mhv)

        return super(SARIce, self).__call__((mhv, green, mhh), *args, **kwargs)