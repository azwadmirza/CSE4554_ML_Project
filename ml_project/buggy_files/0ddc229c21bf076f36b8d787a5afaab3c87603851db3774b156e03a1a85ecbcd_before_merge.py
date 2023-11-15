def calc_stats_dt(srs: dd.Series) -> Dict[str, str]:
    """
    Calculate stats from a datetime column

    Parameters
    ----------
    srs
        a datetime column
    Returns
    -------
    Dict[str, str]
        Dictionary that contains Overview
    """
    size = len(srs)  # include nan
    count = srs.count()  # exclude nan
    uniq_count = srs.nunique()
    overview_dict = {
        "Distinct Count": uniq_count,
        "Unique (%)": uniq_count / count,
        "Missing": size - count,
        "Missing (%)": 1 - (count / size),
        "Memory Size": srs.memory_usage(),
        "Minimum": srs.min(),
        "Maximum": srs.max(),
    }

    return overview_dict