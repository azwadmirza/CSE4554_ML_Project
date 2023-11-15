    def __init__(
        self,
        func: Callable,
        inputs: Union[None, str, List[str], Dict[str, str]],
        outputs: Union[None, str, List[str], Dict[str, str]],
        *,
        name: str = None,
        tags: Union[str, Iterable[str]] = None,
        decorators: Iterable[Callable] = None
    ):
        """Create a node in the pipeline by providing a function to be called
        along with variable names for inputs and/or outputs.

        Args:
            func: A function that corresponds to the node logic.
                The function should have at least one input or output.
            inputs: The name or the list of the names of variables used as
                inputs to the function. The number of names should match
                the number of arguments in the definition of the provided
                function. When Dict[str, str] is provided, variable names
                will be mapped to function argument names.
            outputs: The name or the list of the names of variables used
                as outputs to the function. The number of names should match
                the number of outputs returned by the provided function.
                When Dict[str, str] is provided, variable names will be mapped
                to the named outputs the function returns.
            name: Optional node name to be used when displaying the node in
                logs or any other visualisations.
            tags: Optional set of tags to be applied to the node.
            decorators: Optional list of decorators to be applied to the node.

        Raises:
            ValueError: Raised in the following cases:
                a) When the provided arguments do not conform to
                the format suggested by the type hint of the argument.
                b) When the node produces multiple outputs with the same name.
                c) An input has the same name as an output.

        """

        if not callable(func):
            raise ValueError(
                _node_error_message(
                    "first argument must be a "
                    "function, not `{}`.".format(type(func).__name__)
                )
            )

        if inputs and not isinstance(inputs, (list, dict, str)):
            raise ValueError(
                _node_error_message(
                    "`inputs` type must be one of [String, List, Dict, None], "
                    "not `{}`.".format(type(inputs).__name__)
                )
            )

        if outputs and not isinstance(outputs, (list, dict, str)):
            raise ValueError(
                _node_error_message(
                    "`outputs` type must be one of [String, List, Dict, None], "
                    "not `{}`.".format(type(outputs).__name__)
                )
            )

        if not inputs and not outputs:
            raise ValueError(
                _node_error_message("it must have some `inputs` or `outputs`.")
            )

        self._validate_inputs(func, inputs)

        self._func = func
        self._inputs = inputs
        self._outputs = outputs
        self._name = name
        self._tags = set(_to_list(tags))
        self._decorators = list(decorators or [])

        self._validate_unique_outputs()
        self._validate_inputs_dif_than_outputs()