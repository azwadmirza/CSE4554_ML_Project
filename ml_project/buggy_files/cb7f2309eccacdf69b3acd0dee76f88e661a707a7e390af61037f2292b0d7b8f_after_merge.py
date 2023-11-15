def _first_valid_index(arr):
    # argmax scans from left
    return notnull(arr).argmax() if len(arr) else 0