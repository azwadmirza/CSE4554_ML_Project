def pie_viz(
    df: pd.DataFrame, nrows: int, col: str, plot_width: int, plot_height: int,
) -> Panel:
    """
    Render a pie chart
    """
    npresent = df[col].sum()
    if nrows > npresent:
        df = df.append(pd.DataFrame({col: [nrows - npresent]}, index=["Others"]))
    df["pct"] = df[col] / nrows * 100
    df["angle"] = df[col] / npresent * 2 * np.pi

    tooltips = [(col, "@index"), ("Count", f"@{col}"), ("Percent", "@pct{0.2f}%")]
    fig = Figure(
        plot_width=plot_width,
        plot_height=plot_height,
        title=col,
        toolbar_location=None,
        tools="hover",
        tooltips=tooltips,
    )
    color_list = CATEGORY20 * (len(df) // len(CATEGORY20) + 1)
    df["colour"] = color_list[0 : len(df)]
    df.index = df.index.astype(str)
    df.index = df.index.map(lambda x: x[0:13] + "..." if len(x) > 13 else x)

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
    legend = Legend(items=[LegendItem(label=dict(field="index"), renderers=[pie])])
    legend.label_text_font_size = "8pt"
    fig.add_layout(legend, "right")
    tweak_figure(fig, "pie")
    fig.axis.major_label_text_font_size = "0pt"
    fig.axis.major_tick_line_color = None
    return Panel(child=row(fig), title="Pie Chart")