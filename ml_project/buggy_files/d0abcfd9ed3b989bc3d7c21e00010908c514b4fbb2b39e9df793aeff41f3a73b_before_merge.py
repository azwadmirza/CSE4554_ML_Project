def isenumclass(x):
    """Check if the object is subclass of enum."""
    if enum is None:
        return False
    return issubclass(x, enum.Enum)