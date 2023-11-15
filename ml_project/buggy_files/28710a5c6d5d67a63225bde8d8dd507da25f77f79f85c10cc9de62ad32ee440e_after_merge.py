    def create_line(self, from_: Optional[str], imports: Set[str]) -> str:
        if from_:
            line = f'from {from_} '
            line += f"import {', '.join(self._set_alias(from_, imports))}"
            return line
        return '\n'.join(f'import {i}' for i in self._set_alias(from_, imports))