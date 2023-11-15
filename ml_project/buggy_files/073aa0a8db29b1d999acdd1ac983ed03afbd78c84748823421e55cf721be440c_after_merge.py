    def compute(self, data, **kwargs):
        """Call the resampling."""
        LOG.debug("Resampling %s", str(data.name))
        results = []
        if data.ndim == 3:
            for _i in range(data.shape[0]):
                res = self.resampler.get_count()
                results.append(res)
        else:
            res = self.resampler.get_count()
            results.append(res)

        return da.stack(results)