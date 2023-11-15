    def pinned_requirements(path):
        # type: (Path) -> Iterator[Tuple[str, str]]
        for line in path.read_text().splitlines():
            one, two = line.split("==", 1)
            name = one.strip()
            version = two.split("#")[0].strip()
            yield name, version