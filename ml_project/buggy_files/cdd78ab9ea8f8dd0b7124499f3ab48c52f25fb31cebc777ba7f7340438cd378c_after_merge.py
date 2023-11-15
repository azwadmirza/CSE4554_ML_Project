    def as_pil(self) -> ImagePIL:
        """Get the image as an instance of :class:`PIL.Image`.

        .. note:: Values will be clamped to 0-255 and cast to uint8.
        """
        self.check_is_2d()
        tensor = self.data
        if len(tensor) == 1:
            tensor = torch.cat(3 * [tensor])
        if len(tensor) != 3:
            raise RuntimeError('The image must have 1 or 3 channels')
        tensor = tensor.permute(3, 1, 2, 0)[0]
        array = tensor.clamp(0, 255).numpy()
        return ImagePIL.fromarray(array.astype(np.uint8))