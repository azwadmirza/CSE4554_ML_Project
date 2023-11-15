    def __call__(self, projectables, *args, **kwargs):
        try:

            vis06 = projectables[0]
            vis08 = projectables[1]
            hrv = projectables[2]

            try:
                ch3 = 3 * hrv - vis06 - vis08
                ch3.attrs = hrv.attrs
            except ValueError as err:
                raise IncompatibleAreas

            ndvi = (vis08 - vis06) / (vis08 + vis06)
            ndvi = np.where(ndvi < 0, 0, ndvi)

            ch1 = ndvi * vis06 + (1 - ndvi) * vis08
            ch1.attrs = vis06.attrs
            ch2 = ndvi * vis08 + (1 - ndvi) * vis06
            ch2.attrs = vis08.attrs

            res = RGBCompositor.__call__(self, (ch1, ch2, ch3),
                                         *args, **kwargs)
        except ValueError:
            raise IncompatibleAreas
        return res