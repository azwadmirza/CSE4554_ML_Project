    def create_line(cls, from_: Optional[str], imports: Set[str]) -> str:
        line: str = ''
        if from_:  # pragma: no cover
            line = f'from {from_} '
        line += f"import {', '.join(sorted(imports))}"
        return line