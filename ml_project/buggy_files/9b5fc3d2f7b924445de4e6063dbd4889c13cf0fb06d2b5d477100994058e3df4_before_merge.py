    def __init__(self, raw: str, allow_short_req_file: bool = True, root: Optional[Path] = None) -> None:
        self._root = Path().cwd() if root is None else root
        if allow_short_req_file:  # patch for tox<4 supporting requirement/constraint files via -rreq.txt/-creq.txt
            lines: List[str] = []
            for line in raw.splitlines():
                if len(line) >= 3 and (line.startswith("-r") or line.startswith("-c")) and not line[2].isspace():
                    line = f"{line[:2]} {line[2:]}"
                lines.append(line)
            adjusted = "\n".join(lines)
            raw = f"{adjusted}\n" if raw.endswith("\\\n") else adjusted  # preserve trailing newline if input has it
        self._raw = raw