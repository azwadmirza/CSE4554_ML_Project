def format_basic(df: dd.DataFrame) -> Dict[str, Any]:
    # pylint: disable=too-many-statements
    """
    Format basic version.

    Parameters
    ----------
    df
        The DataFrame for which data are calculated.

    Returns
    -------
    Dict[str, Any]
        A dictionary in which formatted data is stored.
        This variable acts like an API in passing data to the template engine.
    """
    # pylint: disable=too-many-locals
    # aggregate all computations
    data, completions = basic_computations(df)

    with catch_warnings():
        filterwarnings(
            "ignore",
            "invalid value encountered in true_divide",
            category=RuntimeWarning,
        )
        (data,) = dask.compute(data)

    # results dictionary
    res: Dict[str, Any] = {}

    # overview
    data["ov"].pop("ks_tests")
    res["overview"] = format_ov_stats(data["ov"])

    # variables
    res["variables"] = {}
    for col in df.columns:
        stats: Any = None  # needed for pylint
        if is_dtype(detect_dtype(df[col]), Continuous()):
            itmdt = Intermediate(col=col, data=data[col], visual_type="numerical_column")
            rndrd = render(itmdt, plot_height_lrg=250, plot_width_lrg=280)["layout"]
            stats = format_num_stats(data[col])
        elif is_dtype(detect_dtype(df[col]), Nominal()):
            itmdt = Intermediate(col=col, data=data[col], visual_type="categorical_column")
            rndrd = render(itmdt, plot_height_lrg=250, plot_width_lrg=280)["layout"]
            stats = format_cat_stats(
                data[col]["stats"], data[col]["len_stats"], data[col]["letter_stats"]
            )
        figs: List[Figure] = []
        for tab in rndrd:
            try:
                fig = tab.children[0]
            except AttributeError:
                fig = tab
            # fig.title = Title(text=tab.title, align="center")
            figs.append(fig)
        res["variables"][col] = {
            "tabledata": stats,
            "plots": components(figs),
            "col_type": itmdt.visual_type.replace("_column", ""),
        }

    if len(data["num_cols"]) > 0:
        # interactions
        res["has_interaction"] = True
        itmdt = Intermediate(data=data["scat"], visual_type="correlation_crossfilter")
        rndrd = render_correlation(itmdt)
        rndrd.sizing_mode = "stretch_width"
        res["interactions"] = components(rndrd)

        # correlations
        res["has_correlation"] = True
        dfs: Dict[str, pd.DataFrame] = {}
        for method, corr in data["corrs"].items():
            ndf = pd.DataFrame(
                {
                    "x": data["num_cols"][data["cordx"]],
                    "y": data["num_cols"][data["cordy"]],
                    "correlation": corr.ravel(),
                }
            )
            dfs[method.name] = ndf[data["cordy"] > data["cordx"]]
        itmdt = Intermediate(
            data=dfs,
            axis_range=list(data["num_cols"]),
            visual_type="correlation_heatmaps",
        )
        rndrd = render_correlation(itmdt)
        figs.clear()
        for tab in rndrd.tabs:
            fig = tab.child
            fig.sizing_mode = "stretch_width"
            fig.title = Title(text=tab.title, align="center", text_font_size="20px")
            figs.append(fig)
        res["correlations"] = components(figs)
    else:
        res["has_interaction"], res["has_correlation"] = False, False

    # missing
    res["has_missing"] = True
    itmdt = completions["miss"](data["miss"])

    rndrd = render_missing(itmdt)
    figs.clear()
    for fig in rndrd["layout"]:
        fig.sizing_mode = "stretch_width"
        fig.title = Title(
            text=rndrd["meta"][rndrd["layout"].index(fig)], align="center", text_font_size="20px"
        )
        figs.append(fig)
    res["missing"] = components(figs)

    return res