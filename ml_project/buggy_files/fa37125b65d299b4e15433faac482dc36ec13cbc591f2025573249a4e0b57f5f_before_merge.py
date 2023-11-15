def grid_qubit_from_proto_id(proto_id: str) -> 'cirq.GridQubit':
    """Parse a proto id to a `cirq.GridQubit`.

    Proto ids for grid qubits are of the form `{row}_{col}` where `{row}` is
    the integer row of the grid qubit, and `{col}` is the integer column of
    the qubit.

    Args:
        proto_id: The id to convert.

    Returns:
        A `cirq.GridQubit` corresponding to the proto id.

    Raises:
        ValueError: If the string not of the correct format.
    """
    parts = proto_id.split('_')
    if len(parts) != 2:
        raise ValueError(
            'GridQubit proto id must be of the form <int>_<int> but was {}'.
            format(proto_id))
    try:
        row, col = parts
        return devices.GridQubit(row=int(row), col=int(col))
    except ValueError:
        raise ValueError(
            'GridQubit proto id must be of the form <int>_<int> but was {}'.
            format(proto_id))