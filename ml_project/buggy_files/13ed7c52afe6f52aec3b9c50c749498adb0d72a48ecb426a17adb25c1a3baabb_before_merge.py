    def _find_definition(self):
        # try and find a def, go backwards from error line
        fn_name = None
        lines = self.get_lines()
        for x in reversed(lines[:self.line - 1]):
            if 'def ' in x:
                fn_name = x
                break

        return fn_name