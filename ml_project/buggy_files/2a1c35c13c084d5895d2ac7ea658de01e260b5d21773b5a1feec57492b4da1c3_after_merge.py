    def validate_and_expand(self) -> List[str]:
        raw = self._normalize_raw()
        result: List[str] = []
        ini_dir = self.root
        for at, line in enumerate(raw.splitlines(), start=1):
            line = re.sub(r"(?<!\\)\s#.*", "", line).strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("-"):
                self._expand_flag(ini_dir, line, result)
            else:
                self._expand_non_flag(at, ini_dir, line, result)
        return result