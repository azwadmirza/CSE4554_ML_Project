    def __init__(self, Z: TensorData, name: Optional[str] = None):
        """
        :param Z: the initial positions of the inducing points, size [M, D]
        """
        super().__init__(name=name)
        self.Z = Parameter(Z, dtype=default_float())