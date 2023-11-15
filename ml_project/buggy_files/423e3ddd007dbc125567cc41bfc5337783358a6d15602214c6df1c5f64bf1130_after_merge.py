    def validate_and_expand(self) -> List[str]:
        raw = self._normalize_raw()
        result: List[str] = []
        ini_dir = self.root
        for at, line in enumerate(raw.splitlines(), start=1):
            if line.startswith("#"):
                continue
            line = re.sub(r"\s#.*", "", line).strip()
            if not line:
                continue
            if line.startswith("-"):  # handle flags
                words = [i for i in re.split(r"(?<!\\)\s", line) if i]
                first = words[0]
                if first in self.VALID_OPTIONS["no_arg"]:
                    if len(words) != 1:
                        raise ValueError(line)
                    else:
                        result.append(" ".join(words))
                elif first in self.VALID_OPTIONS["one_arg"]:
                    if len(words) != 2:
                        raise ValueError(line)
                    else:
                        if first in ("-r", "--requirement", "-c", "--constraint"):
                            raw_path = line[len(first) + 1 :].strip()
                            unescaped_path = re.sub(r"\\(\s)", r"\1", raw_path)
                            path = Path(unescaped_path)
                            if not path.is_absolute():
                                path = ini_dir / path
                            if not path.exists():
                                raise ValueError(f"requirement file path {str(path)!r} does not exist")
                            req_file = RequirementsFile(path.read_text(), within_tox_ini=False, root=self.root)
                            result.extend(req_file.validate_and_expand())
                        else:
                            result.append(" ".join(words))
                else:
                    raise ValueError(line)
            else:
                try:
                    req = Requirement(line)
                    result.append(str(req))
                except InvalidRequirement as exc:
                    if is_url(line) or any(line.startswith(f"{v}+") and is_url(line[len(v) + 1 :]) for v in VCS):
                        result.append(line)
                    else:
                        path = ini_dir / line
                        try:
                            is_valid_file = path.exists() and path.is_file()
                        except OSError:  # https://bugs.python.org/issue42855 # pragma: no cover
                            is_valid_file = False  # pragma: no cover
                        if not is_valid_file:
                            raise ValueError(f"{at}: {line}") from exc
                        result.append(str(path))
        return result