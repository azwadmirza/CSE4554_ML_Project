def render_cat(
    itmdt: Intermediate, yscale: str, plot_width: int, plot_height: int
) -> Tabs:
    """
    Render plots from plot(df, x) when x is a categorical column
    """
    tabs: List[Panel] = []
    osd = itmdt["statsdata"]
    tabs.append(stats_viz_cat(osd, plot_width, plot_height))
    df, total_grps, miss_pct = itmdt["data"]
    fig = bar_viz(
        df[:-1],
        total_grps,
        miss_pct,
        itmdt["col"],
        yscale,
        plot_width,
        plot_height,
        True,
    )
    tabs.append(Panel(child=row(fig), title="bar chart"))
    tabs.append(pie_viz(df, itmdt["col"], miss_pct, plot_width, plot_height))
    freq_tuple = itmdt["word_cloud"]
    if freq_tuple[0] != 0:
        word_cloud = wordcloud_viz(freq_tuple, plot_width, plot_height)
        tabs.append(Panel(child=row(word_cloud), title="word cloud"))
        wordfreq = wordfreq_viz(freq_tuple, plot_width, plot_height, True)
        tabs.append(Panel(child=row(wordfreq), title="words frequency"))
    df, miss_pct = itmdt["length_dist"]
    length_dist = hist_viz(
        df, miss_pct, "length", yscale, plot_width, plot_height, True
    )
    tabs.append(Panel(child=row(length_dist), title="length"))
    tabs = Tabs(tabs=tabs)

    return tabs