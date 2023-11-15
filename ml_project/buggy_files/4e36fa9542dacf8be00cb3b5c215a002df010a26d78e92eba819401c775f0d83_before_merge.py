    def spawn(
        fn: Callable,
        args: Tuple,
        kwargs_dict: Optional[Mapping] = None,
        num_procs_per_node: int = 1,
        num_nodes: int = 1,
        node_rank: int = 0,
        backend: str = "xla-tpu",
        **kwargs
    ):
        if not has_xla_support:
            raise RuntimeError("Torch xla package is not installed.")

        import os

        if "COLAB_TPU_ADDR" in os.environ:
            kwargs["start_method"] = "fork"

        xmp.spawn(
            _XlaDistModel._dist_worker_task_fn,
            args=(backend, fn, args, kwargs_dict),
            nprocs=num_procs_per_node,
            **kwargs,
        )