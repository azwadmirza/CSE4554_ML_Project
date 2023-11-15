    def _find_definition(self):
        # try and find a def, go backwards from error line
        fn_name = None
        lines = self.get_lines()
        for x in reversed(lines[:self.line - 1]):
            # the strip and startswith is to handle user code with commented out
            # 'def' or use of 'def' in a docstring.
            if x.strip().startswith('def '):
                fn_name = x
                break

        return fn_name