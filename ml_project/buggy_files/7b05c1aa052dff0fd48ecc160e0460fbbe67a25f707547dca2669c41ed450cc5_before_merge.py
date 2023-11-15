    def get_output(value: str) -> None:
        # Drop messages that could be confusing in the Schemathesis context
        if value.startswith(("Falsifying example: ", "You can add @seed")):
            return
        output.append(value)