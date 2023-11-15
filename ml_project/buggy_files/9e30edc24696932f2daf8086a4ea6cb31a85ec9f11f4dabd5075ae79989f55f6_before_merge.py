def one_hot(hot_idx: int, length: int, dtype: Optional[Text] = None) -> np.ndarray:
    if hot_idx >= length:
        raise ValueError(
            "Can't create one hot. Index '{}' is out "
            "of range (length '{}')".format(hot_idx, length)
        )
    r = np.zeros(length, dtype)
    r[hot_idx] = 1
    return r