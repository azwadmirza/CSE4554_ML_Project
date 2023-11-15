    def __init__(
            self,
            num_ghosts: Union[int, Tuple[int, int]] = (4, 10),
            axes: Union[int, Tuple[int, ...]] = (0, 1, 2),
            intensity: Union[float, Tuple[float, float]] = (0.5, 1),
            restore: float = 0.02,
            p: float = 1,
            seed: Optional[int] = None,
            ):
        super().__init__(p=p, seed=seed)
        if not isinstance(axes, tuple):
            try:
                axes = tuple(axes)
            except TypeError:
                axes = (axes,)
        for axis in axes:
            if axis not in (0, 1, 2):
                raise ValueError(f'Axes must be in (0, 1, 2), not "{axes}"')
        self.axes = axes
        if isinstance(num_ghosts, int):
            self.num_ghosts_range = num_ghosts, num_ghosts
        elif isinstance(num_ghosts, tuple) and len(num_ghosts) == 2:
            self.num_ghosts_range = num_ghosts
        self.intensity_range = self.parse_range(intensity, 'intensity')
        for n in self.intensity_range:
            if n < 0:
                message = (
                    f'Intensity must be a positive number, not {n}')
                raise ValueError(message)
        if not 0 <= restore < 1:
            message = (
                f'Restore must be a number between 0 and 1, not {restore}')
            raise ValueError(message)
        self.restore = restore