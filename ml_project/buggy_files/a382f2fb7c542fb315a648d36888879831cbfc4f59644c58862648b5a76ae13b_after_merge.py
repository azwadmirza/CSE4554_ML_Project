    def __init__(
        self,
        constraints,  # type: Iterable[str]
        candidates,  # type: Iterable[PythonInterpreter]
        failures,  # type: Iterable[InterpreterIdentificationError]
        preamble=None,  # type: Optional[str]
    ):
        # type: (...) -> None
        """
        :param constraints: The constraints that could not be satisfied.
        :param candidates: The python interpreters that were compared against the constraints.
        :param failures: Descriptions of the python interpreters that were unidentifiable.
        :param preamble: An optional preamble for the exception message.
        """
        self.constraints = tuple(constraints)
        self.candidates = tuple(candidates)
        self.failures = tuple(failures)
        super(UnsatisfiableInterpreterConstraintsError, self).__init__(
            self.create_message(preamble=preamble)
        )