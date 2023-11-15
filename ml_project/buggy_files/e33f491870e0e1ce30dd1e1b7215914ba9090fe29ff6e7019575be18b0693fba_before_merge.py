def guess_continuous(property: np.ndarray) -> bool:
    """Guess if the property is continuous (return True) or categorical (return False)"""
    # if the property is a floating type, guess continuous
    if issubclass(property.dtype.type, np.floating) and len(property < 16):
        return True
    else:
        return False