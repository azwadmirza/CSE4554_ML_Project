    def __init__(self, raw: str, within_tox_ini: bool = True, root: Optional[Path] = None) -> None:
        self._root = Path().cwd() if root is None else root
        if within_tox_ini:  # patch the content coming from tox.ini
            lines: List[str] = []
            for line in raw.splitlines():
                # for tox<4 supporting requirement/constraint files via -rreq.txt/-creq.txt
                if len(line) >= 3 and (line.startswith("-r") or line.startswith("-c")) and not line[2].isspace():
                    line = f"{line[:2]} {line[2:]}"
                # escape spaces
                escape_for = ("-c", "--constraint", "-r", "--requirement", "-f", "--find-links" "-e", "--editable")
                escape_match = next((e for e in escape_for if line.startswith(e) and line[len(e)].isspace()), None)
                if escape_match is not None:
                    # escape not already escaped spaces
                    escaped = re.sub(r"(?<!\\)(\s)", r"\\\1", line[len(escape_match) + 1 :])
                    line = f"{line[:len(escape_match)]} {escaped}"
                lines.append(line)
            adjusted = "\n".join(lines)
            raw = f"{adjusted}\n" if raw.endswith("\\\n") else adjusted  # preserve trailing newline if input has it
        self._raw = raw