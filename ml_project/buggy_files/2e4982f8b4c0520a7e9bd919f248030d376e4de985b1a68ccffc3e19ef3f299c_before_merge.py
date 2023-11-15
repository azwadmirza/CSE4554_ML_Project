    def from_dataset(cls, dataset, map_crs='epsg:4326'):
        if dataset.crs is None:
            return IdentityCRSTransformer()
        transform = dataset.transform
        image_crs = dataset.crs['init']
        return cls(transform, image_crs, map_crs)