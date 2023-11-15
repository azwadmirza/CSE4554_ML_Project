    def _parse_annotation(self, raw_annotation: Type) -> None:
        """Parse key information from annotation.

        :param annotation: A subscripted type.
        :returns: Annotation
        """
        self.raw_annotation = raw_annotation

        self.optional = typing_inspect.is_optional_type(raw_annotation)
        if self.optional:
            # e.g: Typing.Union[pandera.typing.Index[str], NoneType]
            if _LEGACY_TYPING:  # pragma: no cover
                # get_args -> ((pandera.typing.Index, <class 'str'>), <class 'NoneType'>)
                self.origin, self.arg = typing_inspect.get_args(
                    raw_annotation
                )[0]
            # get_args -> (pandera.typing.Index[str], <class 'NoneType'>)
            raw_annotation = typing_inspect.get_args(raw_annotation)[0]

        if not (self.optional and _LEGACY_TYPING):
            self.origin = typing_inspect.get_origin(raw_annotation)
            args = typing_inspect.get_args(raw_annotation)
            self.arg = args[0] if args else args

        self.literal = typing_inspect.is_literal_type(self.arg)
        if self.literal:
            self.arg = typing_inspect.get_args(self.arg)[0]