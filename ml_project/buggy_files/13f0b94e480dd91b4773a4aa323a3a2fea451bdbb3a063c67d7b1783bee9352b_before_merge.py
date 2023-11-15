    def __init__(self, raw: str, allow_short_req_file: bool = True, root: Optional[Path] = None) -> None:
        self._root = Path().cwd() if root is None else root
        if allow_short_req_file:  # patch tox supporting requirements files via -rrequirements.txt
            r = ((f"-r {i[2:]}" if len(i) >= 3 and i.startswith("-r") and i[2] != " " else i) for i in raw.splitlines())
            adjusted = "\n".join(r)
            raw = f"{adjusted}\n" if raw.endswith("\\\n") else adjusted
        self._raw = raw