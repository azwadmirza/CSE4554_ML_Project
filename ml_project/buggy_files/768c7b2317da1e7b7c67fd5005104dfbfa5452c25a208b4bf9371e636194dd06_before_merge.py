    def __init__(self) -> None:
        self._predictions_labels_covariance = Covariance()
        self._predictions_variance = Covariance()
        self._labels_variance = Covariance()
        self._device = torch.device("cpu")