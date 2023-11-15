def convert_serializable(records):
    # type: (List[logging.LogRecord]) -> None
    """Convert LogRecord serializable."""
    for r in records:
        # extract arguments to a message and clear them
        r.msg = r.getMessage()
        r.args = ()

        location = getattr(r, 'location', None)
        if isinstance(location, nodes.Node):
            r.location = get_node_location(location)  # type: ignore