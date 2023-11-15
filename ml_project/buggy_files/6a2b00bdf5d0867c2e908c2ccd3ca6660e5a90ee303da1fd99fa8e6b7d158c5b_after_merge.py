        def create_from_backend(backend: str = "xla-tpu", **kwargs) -> "_XlaDistModel":
            return _XlaDistModel(backend=backend, **kwargs)