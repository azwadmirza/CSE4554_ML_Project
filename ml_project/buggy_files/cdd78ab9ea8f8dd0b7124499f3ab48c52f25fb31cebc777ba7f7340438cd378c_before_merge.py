    def as_pil(self) -> ImagePIL:
        """Get the image as an instance of :class:`PIL.Image`."""
        self.check_is_2d()
        return ImagePIL.open(self.path)