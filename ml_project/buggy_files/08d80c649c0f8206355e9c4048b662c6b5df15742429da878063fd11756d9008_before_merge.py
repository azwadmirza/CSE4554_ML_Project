def calc_stats_cat(
    srs: dd.Series,
) -> Tuple[Dict[str, str], Dict[str, str], Dict[str, str], Dict[str, str]]:
    """
    Calculate stats from a categorical column
    Parameters
    ----------
    srs
        a categorical column
    Returns
    -------
    Dict[str, str]
        Dictionary that contains Overview
    """
    # overview stats
    size = len(srs)  # include nan
    count = srs.count()  # exclude nan
    uniq_count = srs.nunique()
    overview_dict = {
        "Distinct Count": uniq_count,
        "Unique (%)": uniq_count / count,
        "Missing": size - count,
        "Missing (%)": 1 - (count / size),
        "Memory Size": srs.memory_usage(),
    }
    srs = srs.astype("str")
    # length stats
    length = srs.str.len()
    length_dict = {
        "mean": length.mean(),
        "median": length.median(),
        "minimum": length.min(),
        "maximum": length.max(),
    }
    # quantile stats
    max_lbl_len = 13
    quantile_dict = {}
    for label, centile in zip(
        (
            "Minimum",
            "5-th Percentile",
            "Q1",
            "Median",
            "Q3",
            "95-th Percentile",
            "Maximum",
        ),
        (0, 0.05, 0.25, 0.5, 0.75, 0.95, 1),
    ):
        if round(len(srs) * centile) == 0:
            element = srs[round(len(srs) * centile)]
            if len(element) > max_lbl_len:
                quantile_dict[label] = element[0 : max_lbl_len - 2] + "..."
            else:
                quantile_dict[label] = element
        else:
            element = srs[round(len(srs) * centile) - 1]
            if len(element) > max_lbl_len:
                quantile_dict[label] = element[0 : max_lbl_len - 2] + "..."
            else:
                quantile_dict[label] = element

    # letter stats
    letter_dict = {
        "count": srs.str.count(r"[a-zA-Z]").sum(),
        "Lowercase Letter": srs.str.count(r"[a-z]").sum(),
        "Space Separator": srs.str.count(r"[ ]").sum(),
        "Uppercase Letter": srs.str.count(r"[A-Z]").sum(),
        "Dash Punctuation": srs.str.count(r"[-]").sum(),
        "Decimal Number": srs.str.count(r"[0-9]").sum(),
    }
    return (
        {k: _format_values(k, v) for k, v in overview_dict.items()},
        {k: _format_values(k, v) for k, v in length_dict.items()},
        quantile_dict,
        {k: _format_values(k, v) for k, v in letter_dict.items()},
    )