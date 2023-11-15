def isenumclass(x):
    """Check if the object is subclass of enum."""
    if enum is None:
        return False
    return inspect.isclass(x) and issubclass(x, enum.Enum)