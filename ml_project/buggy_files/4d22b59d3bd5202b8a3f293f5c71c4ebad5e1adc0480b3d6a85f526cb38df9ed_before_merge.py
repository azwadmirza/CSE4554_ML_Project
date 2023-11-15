def _make_eq(cls, attrs):
    """
    Create __eq__ method for *cls* with *attrs*.
    """
    attrs = [a for a in attrs if a.eq]

    unique_filename = _generate_unique_filename(cls, "eq")
    lines = [
        "def __eq__(self, other):",
        "    if other.__class__ is not self.__class__:",
        "        return NotImplemented",
    ]
    # We can't just do a big self.x = other.x and... clause due to
    # irregularities like nan == nan is false but (nan,) == (nan,) is true.
    if attrs:
        lines.append("    return  (")
        others = ["    ) == ("]
        for a in attrs:
            lines.append("        self.%s," % (a.name,))
            others.append("        other.%s," % (a.name,))

        lines += others + ["    )"]
    else:
        lines.append("    return True")

    script = "\n".join(lines)
    globs = {}
    locs = {}
    bytecode = compile(script, unique_filename, "exec")
    eval(bytecode, globs, locs)

    # In order of debuggers like PDB being able to step through the code,
    # we add a fake linecache entry.
    linecache.cache[unique_filename] = (
        len(script),
        None,
        script.splitlines(True),
        unique_filename,
    )
    return locs["__eq__"]