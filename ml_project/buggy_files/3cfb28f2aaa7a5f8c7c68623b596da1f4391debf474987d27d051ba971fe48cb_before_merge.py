def pie_viz(
    df: pd.DataFrame, col: str, miss_pct: float, plot_width: int, plot_height: int,
) -> Panel:
    """
    Render a pie chart
    """
    title = f"{col} ({miss_pct}% missing)" if miss_pct > 0 else f"{col}"
    tooltips = [(f"{col}", "@col"), ("Count", "@cnt"), ("Percent", "@pct{0.2f}%")]
    df["angle"] = df["cnt"] / df["cnt"].sum() * 2 * pi
    fig = Figure(
        title=title,
        plot_width=plot_width,
        plot_height=plot_height,
        tools="hover",
        toolbar_location=None,
        tooltips=tooltips,
    )
    color_list = PALETTE * (len(df) // len(PALETTE) + 1)
    df["colour"] = color_list[0 : len(df)]
    if df.iloc[-1]["cnt"] == 0:  # no "Others" group
        df = df[:-1]
    df["col"] = df["col"].map(lambda x: x[0:13] + "..." if len(x) > 13 else x)
    pie = fig.wedge(
        x=0,
        y=1,
        radius=0.9,
        start_angle=cumsum("angle", include_zero=True),
        end_angle=cumsum("angle"),
        line_color="white",
        fill_color="colour",
        source=df,
    )
    legend = Legend(items=[LegendItem(label=dict(field="col"), renderers=[pie])])
    legend.label_text_font_size = "8pt"
    fig.add_layout(legend, "right")
    tweak_figure(fig, "pie")
    fig.axis.major_label_text_font_size = "0pt"
    fig.axis.major_tick_line_color = None
    return Panel(child=row(fig), title="pie chart")