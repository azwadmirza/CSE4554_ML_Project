def _line_to_path(dwg: svgwrite.Drawing, lines: Union[np.ndarray, LineCollection]):
    """Convert a line into a SVG path element.

    Accepts either a single line or a :py:class:`LineCollection`.

    Args:
        lines: line(s) to convert to path

    Returns:
        (svgwrite element): path element

    """

    if isinstance(lines, np.ndarray):
        lines = [lines]

    def single_line_to_path(line: np.ndarray) -> str:
        if line[0] == line[-1]:
            closed = True
            line = line[:-1]
        else:
            closed = False
        return (
            "M" + " L".join(f"{x},{y}" for x, y in as_vector(line)) + (" Z" if closed else "")
        )

    return dwg.path(" ".join(single_line_to_path(line) for line in lines))