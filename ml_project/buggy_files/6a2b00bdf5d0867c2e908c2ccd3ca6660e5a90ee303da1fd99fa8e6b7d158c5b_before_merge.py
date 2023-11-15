    def create_from_backend(backend: str = "xla-tpu", **kwargs) -> "_XlaDistModel":
        if not has_xla_support:
            raise RuntimeError("Torch xla package is not installed.")
        return _XlaDistModel(backend=backend, **kwargs)