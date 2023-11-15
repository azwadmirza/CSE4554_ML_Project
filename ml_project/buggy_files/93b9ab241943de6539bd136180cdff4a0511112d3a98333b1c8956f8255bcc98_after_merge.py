    def __init__(self, transform, image_crs, map_crs='epsg:4326'):
        """Construct transformer.

        Args:
            image_dataset: Rasterio DatasetReader
            map_crs: CRS code
        """
        self.map_proj = pyproj.Proj(init=map_crs)
        self.image_proj = pyproj.Proj(image_crs)

        super().__init__(image_crs, map_crs, transform)