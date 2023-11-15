def nom_insights(data: Dict[str, Any], col: str) -> Dict[str, List[str]]:
    """
    Format the insights for plot(df, Nominal())
    """
    # pylint: disable=line-too-long
    # insight dictionary, with a list associated with each plot
    ins: Dict[str, List[str]] = {
        "stat": [],
        "bar": [],
        "pie": [],
        "cloud": [],
        "wf": [],
        "wl": [],
    }

    ## if cfg.insight.constant_enable:
    if data["nuniq"] == 1:
        ins["stat"].append(f"{col} has a constant value")

    ## if cfg.insight.high_cardinality_enable:
    if data["nuniq"] > 50:  ## cfg.insght.high_cardinality_threshold
        nuniq = data["nuniq"]
        ins["stat"].append(f"{col} has a high cardinality: {nuniq} distinct values")

    ## if cfg.insight.missing_enable:
    pmiss = round((data["nrows"] - data["stats"]["npres"]) / data["nrows"] * 100, 2)
    if pmiss > 1:  ## cfg.insight.missing_threshold
        nmiss = data["nrows"] - data["stats"]["npres"]
        ins["stat"].append(f"{col} has {nmiss} ({pmiss}%) missing values")

    ## if cfg.insight.constant_length_enable:
    if data["stats"]["nuniq"] == data["stats"]["npres"]:
        ins["stat"].append(f"{col} has all distinct values")

    ## if cfg.insight.evenness_enable:
    if data["chisq"][1] > 0.999:  ## cfg.insight.uniform_threshold
        ins["bar"].append(f"{col} is relatively evenly distributed")

    ## if cfg.insight.outstanding_no1_enable
    factor = data["bar"][0] / data["bar"][1] if len(data["bar"]) > 1 else 0
    if factor > 1.5:
        val1, val2 = data["bar"].index[0], data["bar"].index[1]
        ins["bar"].append(
            f"The largest value ({val1}) is over {factor} times larger than the second largest value ({val2})"
        )

    ## if cfg.insight.attribution_enable
    if data["pie"][:2].sum() / data["nrows"] > 0.5 and len(data["pie"]) >= 2:
        vals = ", ".join(data["pie"].index[i] for i in range(2))
        ins["pie"].append(f"The top 2 categories ({vals}) take over 50%")

    ## if cfg.insight.high_word_cardinlaity_enable
    if data["nwords"] > 1000:
        nwords = data["nwords"]
        ins["cloud"].append(f"{col} contains many words: {nwords} words")

    ## if cfg.insight.outstanding_no1_word_enable
    factor = (
        data["word_cnts"][0] / data["word_cnts"][1] if len(data["word_cnts"]) > 1 else 0
    )
    if factor > 1.5:
        val1, val2 = data["word_cnts"].index[0], data["word_cnts"].index[1]
        ins["wf"].append(
            f"The largest value ({val1}) is over {factor} times larger than the second largest value ({val2})"
        )

    ## if cfg.insight.constant_word_length_enable
    if data["len_stats"]["Minimum"] == data["len_stats"]["Maximum"]:
        ins["wf"].append(f"{col} has words of constant length")

    return ins