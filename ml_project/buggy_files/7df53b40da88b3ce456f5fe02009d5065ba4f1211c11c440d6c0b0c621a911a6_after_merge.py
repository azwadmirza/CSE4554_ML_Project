    def validate_and_convert_to_enum(
        enum_type: Type[Enum], value: Any, allow_none: bool = True
    ) -> Optional[Enum]:
        if allow_none and value is None:
            return None

        if not isinstance(value, (str, int)) and not isinstance(value, enum_type):
            raise ValidationError(
                f"Value $VALUE ($VALUE_TYPE) is not a valid input for {enum_type}"
            )

        if isinstance(value, enum_type):
            return value

        try:
            if isinstance(value, (float, bool)):
                raise ValueError

            if isinstance(value, int):
                return enum_type(value)

            if isinstance(value, str):
                prefix = f"{enum_type.__name__}."
                if value.startswith(prefix):
                    value = value[len(prefix) :]
                return enum_type[value]

            assert False

        except (ValueError, KeyError) as e:
            valid = ", ".join([x for x in enum_type.__members__.keys()])
            raise ValidationError(
                f"Invalid value '$VALUE', expected one of [{valid}]"
            ).with_traceback(sys.exc_info()[2]) from e