    def single_line_to_path(line: np.ndarray) -> str:
        if line[0] == line[-1]:
            closed = True
            line = line[:-1]
        else:
            closed = False
        return (
            "M" + " L".join(f"{x},{y}" for x, y in as_vector(line)) + (" Z" if closed else "")
        )