def convert_serializable(records):
    # type: (List[logging.LogRecord]) -> None
    """Convert LogRecord serializable."""
    for r in records:
        # extract arguments to a message and clear them
        r.msg = r.getMessage()
        r.args = ()