    def __call__(self, datasets, optional_datasets=None, **info):
        if len(datasets) != 3:
            raise ValueError("Expected 3 datasets, got %d" % (len(datasets), ))

        area = None
        n = {}
        p1, p2, p3 = datasets
        if optional_datasets:
            high_res = optional_datasets[0]
            low_res = datasets[["red", "green", "blue"].index(
                self.high_resolution_band)]
            if high_res.info["area"] != low_res.info["area"]:
                if np.mod(high_res.shape[0], low_res.shape[0]) or \
                        np.mod(high_res.shape[1], low_res.shape[1]):
                    raise IncompatibleAreas(
                        "High resolution band is not mapped the same area as the low resolution bands")
                else:
                    f0 = high_res.shape[0] / low_res.shape[0]
                    f1 = high_res.shape[1] / low_res.shape[1]
                    if p1.shape != high_res.shape:
                        p1 = np.ma.repeat(np.ma.repeat(
                            p1, f0, axis=0), f1, axis=1)
                        p1.info["area"] = high_res.info["area"]
                    if p2.shape != high_res.shape:
                        p2 = np.ma.repeat(np.ma.repeat(
                            p2, f0, axis=0), f1, axis=1)
                        p2.info["area"] = high_res.info["area"]
                    if p3.shape != high_res.shape:
                        p3 = np.ma.repeat(np.ma.repeat(
                            p3, f0, axis=0), f1, axis=1)
                        p3.info["area"] = high_res.info["area"]
                    area = high_res.info["area"]
            if 'rows_per_scan' in high_res.info:
                n.setdefault('rows_per_scan', high_res.info['rows_per_scan'])
            n.setdefault('resolution', high_res.info['resolution'])
            if self.high_resolution_band == "red":
                LOG.debug("Sharpening image with high resolution red band")
                ratio = high_res.data / p1.data
                r = high_res.data
                g = p2.data * ratio
                b = p3.data * ratio
            elif self.high_resolution_band == "green":
                LOG.debug("Sharpening image with high resolution green band")
                ratio = high_res.data / p2.data
                r = p1.data * ratio
                g = high_res.data
                b = p3.data * ratio
            elif self.high_resolution_band == "blue":
                LOG.debug("Sharpening image with high resolution blue band")
                ratio = high_res.data / p3.data
                r = p1.data * ratio
                g = p2.data * ratio
                b = high_res.data
            else:
                # no sharpening
                r = p1.data
                g = p2.data
                b = p3.data
            mask = p1.mask | p2.mask | p3.mask | high_res.mask
        else:
            r, g, b = p1.data, p2.data, p3.data
            mask = p1.mask | p2.mask | p3.mask

        # Collect information that is the same between the projectables
        info = combine_metadata(*datasets)
        info.update(n)
        # Update that information with configured information (including name)
        info.update(self.attrs)
        # Force certain pieces of metadata that we *know* to be true
        info["wavelength"] = None
        info.setdefault("standard_name", "true_color")
        info["mode"] = self.attrs.get("mode", "RGB")
        if area is not None:
            info['area'] = area
        return Dataset(data=np.concatenate(
            ([r], [g], [b]), axis=0),
            mask=np.array([[mask, mask, mask]]),
            **info)