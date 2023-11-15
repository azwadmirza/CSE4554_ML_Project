    def __call__(self, data):
        d = dict(data)
        for idx, key in enumerate(self.keys):
            meta_data = d[f"{key}_{self.meta_key_postfix}"]
            # resample array of each corresponding key
            # using affine fetched from d[affine_key]
            d[key], _, new_affine = self.spacing_transform(
                data_array=d[key],
                affine=meta_data["affine"],
                mode=self.mode[idx],
                padding_mode=self.padding_mode[idx],
                dtype=self.dtype[idx],
            )
            # set the 'affine' key
            meta_data["affine"] = new_affine
        return d