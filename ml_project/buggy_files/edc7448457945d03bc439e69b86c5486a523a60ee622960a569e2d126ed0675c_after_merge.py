    def get_writer_by_ext(self, extension, **kwargs):
        """Find the writer matching the *extension*."""
        mapping = {".tiff": "geotiff", ".tif": "geotiff", ".nc": "cf"}
        return self.get_writer(
            mapping.get(extension.lower(), "simple_image"), **kwargs)