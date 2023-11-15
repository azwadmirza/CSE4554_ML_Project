def wordcloud_viz(word_cnts: pd.Series, plot_width: int, plot_height: int,) -> Panel:
    """
    Visualize the word cloud
    """  # pylint: disable=unsubscriptable-object
    ellipse_mask = np.array(
        Image.open(f"{Path(__file__).parent.parent.parent}/assets/ellipse.jpg")
    )
    wordcloud = WordCloud(
        background_color="white", mask=ellipse_mask, width=800, height=400
    )
    wordcloud.generate_from_frequencies(word_cnts)
    wcimg = wordcloud.to_array().astype(np.uint8)
    alpha = np.full([*wcimg.shape[:2], 1], 255, dtype=np.uint8)
    wcimg = np.concatenate([wcimg, alpha], axis=2)[::-1, :]

    fig = figure(
        plot_width=plot_width,
        plot_height=plot_height,
        title="Word Cloud",
        x_range=(0, 1),
        y_range=(0, 1),
        toolbar_location=None,
    )
    fig.image_rgba(image=[wcimg], x=0, y=0, dh=1, dw=1)

    fig.axis.visible = False
    fig.grid.visible = False
    return Panel(child=row(fig), title="Word Cloud")