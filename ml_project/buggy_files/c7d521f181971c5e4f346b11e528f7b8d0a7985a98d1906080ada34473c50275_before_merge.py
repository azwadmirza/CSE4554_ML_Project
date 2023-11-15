    def _is_valid_final_value(self, format_value: ast.AST) -> bool:
        # Variable lookup is okay and a single attribute is okay
        if isinstance(format_value, (ast.Name, ast.Attribute)):
            return True
        # Function call with empty arguments is okay
        elif isinstance(format_value, ast.Call) and not format_value.args:
            return True
        # Named lookup, Index lookup & Dict key is okay
        elif isinstance(format_value, ast.Subscript):
            if isinstance(format_value.slice, ast.Index):
                return isinstance(
                    format_value.slice.value,
                    self._valid_format_index,
                )
        return False