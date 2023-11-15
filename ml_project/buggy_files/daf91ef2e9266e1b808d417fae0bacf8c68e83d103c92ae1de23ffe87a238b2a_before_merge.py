    def __init__(
        self,
        freq: str,
        prediction_length: int,
        method_name: str = "ets",
        period: int = None,
        trunc_length: Optional[int] = None,
        params: Optional[Dict] = None,
    ) -> None:
        super().__init__(freq=freq, prediction_length=prediction_length)

        try:
            from rpy2 import robjects, rinterface
            import rpy2.robjects.packages as rpackages
            from rpy2.rinterface import RRuntimeError
        except ImportError as e:
            raise ImportError(str(e) + USAGE_MESSAGE) from e

        self._robjects = robjects
        self._rinterface = rinterface
        self._rinterface.initr()
        self._rpackages = rpackages

        this_dir = os.path.dirname(os.path.realpath(__file__))
        this_dir = this_dir.replace("\\", "/")  # for windows
        r_files = [
            n[:-2] for n in os.listdir(f"{this_dir}/R/") if n[-2:] == ".R"
        ]

        for n in r_files:
            try:
                robjects.r(f'source("{this_dir}/R/{n}.R")')
            except RRuntimeError as er:
                raise RRuntimeError(str(er) + USAGE_MESSAGE) from er

        supported_methods = ["ets", "arima", "tbats", "croston", "mlp"]
        assert (
            method_name in supported_methods
        ), f"method {method_name} is not supported please use one of {supported_methods}"

        self.method_name = method_name

        self._stats_pkg = rpackages.importr("stats")
        self._r_method = robjects.r[method_name]

        self.prediction_length = prediction_length
        self.freq = freq
        self.period = period if period is not None else get_seasonality(freq)
        self.trunc_length = trunc_length

        self.params = {
            "prediction_length": self.prediction_length,
            "output_types": ["samples"],
            "frequency": self.period,
        }
        if params is not None:
            self.params.update(params)