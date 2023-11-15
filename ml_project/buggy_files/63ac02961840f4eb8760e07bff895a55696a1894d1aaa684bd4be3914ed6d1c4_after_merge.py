    def create_line(cls, from_: Optional[str], imports: Set[str]) -> str:
        if from_:
            line = f'from {from_} '
            line += f"import {', '.join(sorted(imports))}"
            return line
        return '\n'.join(f'import {i}\n' for i in sorted(imports))