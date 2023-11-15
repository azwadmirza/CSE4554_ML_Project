    def get_literal_value(value):
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError, TypeError):
            return value