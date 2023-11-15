    def convert_input(self, value):
        # Keep string here.
        if isinstance(value, str):
            return value, False
        else:
            return super().convert_input(value)