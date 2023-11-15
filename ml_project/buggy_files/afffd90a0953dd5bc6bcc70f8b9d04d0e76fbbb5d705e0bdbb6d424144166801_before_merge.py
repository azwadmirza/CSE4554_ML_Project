    def __call__(self, projectables, *args, **kwargs):
        try:

            vis06 = projectables[0]
            vis08 = projectables[1]
            hrv = projectables[2]

            ndvi = (vis08 - vis06) / (vis08 + vis06)
            ndvi = np.where(ndvi < 0, 0, ndvi)

            # info = combine_info(*projectables)
            # info['name'] = self.info['name']
            # info['standard_name'] = self.info['standard_name']

            ch1 = Dataset(ndvi * vis06 + (1 - ndvi) * vis08,
                          copy=False,
                          **vis06.info)
            ch2 = Dataset(ndvi * vis08 + (1 - ndvi) * vis06,
                          copy=False,
                          **vis08.info)
            ch3 = Dataset(3 * hrv - vis06 - vis08,
                          copy=False,
                          **hrv.info)

            res = RGBCompositor.__call__(self, (ch1, ch2, ch3),
                                         *args, **kwargs)
        except ValueError:
            raise IncompatibleAreas
        return res