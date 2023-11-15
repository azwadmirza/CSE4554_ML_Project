    def __init__(self, field_name: str, annotation):
        message = (
            f'The type "{annotation}" of the field "{field_name}" '
            f"is generic, but no type has been passed"
        )

        super().__init__(message)