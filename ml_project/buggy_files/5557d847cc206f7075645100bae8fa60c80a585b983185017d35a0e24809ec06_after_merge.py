    def output_pixels(self) -> Optional[int]:
        """Number of pixels for a single feature map (1 for fully connected layers)."""
        if not self.output_shape:
            return None
        if len(self.output_shape) == 4:
            return int(np.prod(self.output_shape[1:3]))
        if len(self.output_shape) == 2:
            return 1
        raise NotImplementedError()