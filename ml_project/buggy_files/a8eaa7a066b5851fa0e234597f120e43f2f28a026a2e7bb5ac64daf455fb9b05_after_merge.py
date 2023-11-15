def _f1(precision: float, recall: float) -> float:
    """
    Compute f1.

    :param float precision
    :param float recall

    :return: f1
    :rtype: float
    """
    if precision == recall == 0:
        return 0
    return 2 * precision * recall / (precision + recall)