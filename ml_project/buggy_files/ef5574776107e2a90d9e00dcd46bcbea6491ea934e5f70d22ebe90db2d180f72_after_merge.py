    def _expand_non_flag(self, at: int, ini_dir: Path, line: str, result: List[str]) -> None:  # noqa
        try:
            at = line.index(" --hash")
            requirement, hash_part = line[:at], re.sub(r"\s+", " ", line[at + 1 :])
        except ValueError:
            requirement, hash_part = line, ""
        try:
            req = Requirement(requirement)
        except InvalidRequirement as exc:
            if is_url(line) or any(line.startswith(f"{v}+") and is_url(line[len(v) + 1 :]) for v in VCS):
                result.append(line)
            else:
                path = ini_dir / line
                try:
                    is_valid_file = path.exists() and (path.is_file() or path.is_dir())
                except OSError:  # https://bugs.python.org/issue42855 # pragma: no cover
                    is_valid_file = False  # pragma: no cover
                if not is_valid_file:
                    raise ValueError(f"{at}: {line}") from exc
                result.append(str(path))
        else:
            entry = str(req)
            if hash_part:
                entry = f"{entry} {hash_part}"
            result.append(entry)