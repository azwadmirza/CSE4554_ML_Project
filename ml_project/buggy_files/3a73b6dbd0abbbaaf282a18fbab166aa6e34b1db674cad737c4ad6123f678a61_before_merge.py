    def __init__(
        self,
        *,
        python_callable: Callable,
        task_id: str,
        op_args: Tuple[Any],
        op_kwargs: Dict[str, Any],
        multiple_outputs: bool = False,
        **kwargs,
    ) -> None:
        kwargs['task_id'] = self._get_unique_task_id(task_id, kwargs.get('dag'))
        super().__init__(**kwargs)
        self.python_callable = python_callable

        # Check that arguments can be binded
        signature(python_callable).bind(*op_args, **op_kwargs)
        self.multiple_outputs = multiple_outputs
        self.op_args = op_args
        self.op_kwargs = op_kwargs