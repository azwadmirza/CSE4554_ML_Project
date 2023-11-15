def find_a_system_python(line):
    """Find a Python installation from a given line.

    This tries to parse the line in various of ways:

    * Looks like an absolute path? Use it directly.
    * Looks like a py.exe call? Use py.exe to get the executable.
    * Starts with "py" something? Looks like a python command. Try to find it
      in PATH, and use it directly.
    * Search for "python" and "pythonX.Y" executables in PATH to find a match.
    * Nothing fits, return None.
    """
    if not line:
        return None
    if os.path.isabs(line):
        return line
    from .vendor.pythonfinder import Finder

    finder = Finder(system=False, global_search=True)
    if (line.startswith("py ") or line.startswith("py.exe ")) and os.name == "nt":
        line = line.split(" ", 1)[1].lstrip("-")
    elif line.startswith("py"):
        python_entry = finder.which(line)
        if python_entry:
            return python_entry.path.as_posix()
        return None
    python_entry = finder.find_python_version(line)
    if not python_entry:
        python_entry = finder.which("python{0}".format(line))
    if python_entry:
        return python_entry.path.as_posix()
    return None