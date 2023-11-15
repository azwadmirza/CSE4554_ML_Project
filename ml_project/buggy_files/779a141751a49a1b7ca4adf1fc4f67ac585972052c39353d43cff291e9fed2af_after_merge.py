def normalize_index(index):
    """
    Flatten a component index.  If it has length 1, then
    return just the element.  If it has length > 1, then
    return a tuple.
    """
    ans = flatten(index)
    if len(ans) == 1:
        return ans[0]
    return ans