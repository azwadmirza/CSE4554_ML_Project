    def __init__(self, raw: str, within_tox_ini: bool = True, root: Optional[Path] = None) -> None:
        self._root = Path().cwd() if root is None else root.resolve()
        if within_tox_ini:  # patch the content coming from tox.ini
            lines: List[str] = []
            for line in raw.splitlines():
                # for tox<4 supporting requirement/constraint files via -rreq.txt/-creq.txt
                arg_match = next(
                    (
                        arg
                        for arg in ONE_ARG
                        if line.startswith(arg)
                        and len(line) > len(arg)
                        and not (line[len(arg)].isspace() or line[len(arg)] == "=")
                    ),
                    None,
                )
                if arg_match is not None:
                    line = f"{arg_match} {line[len(arg_match):]}"
                # escape spaces
                escape_match = next((e for e in ONE_ARG_ESCAPE if line.startswith(e) and line[len(e)].isspace()), None)
                if escape_match is not None:
                    # escape not already escaped spaces
                    escaped = re.sub(r"(?<!\\)(\s)", r"\\\1", line[len(escape_match) + 1 :])
                    line = f"{line[:len(escape_match)]} {escaped}"
                lines.append(line)
            adjusted = "\n".join(lines)
            raw = f"{adjusted}\n" if raw.endswith("\\\n") else adjusted  # preserve trailing newline if input has it
        self._raw = raw