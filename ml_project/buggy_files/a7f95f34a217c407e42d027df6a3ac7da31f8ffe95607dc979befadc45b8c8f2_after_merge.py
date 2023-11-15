    def __init__(self, bin_centers: List[float]) -> None:
        # cannot pass directly nd.array because it is not serializable
        bc = mx.nd.array(bin_centers)
        assert len(bc.shape) == 1
        self.bin_centers = bc