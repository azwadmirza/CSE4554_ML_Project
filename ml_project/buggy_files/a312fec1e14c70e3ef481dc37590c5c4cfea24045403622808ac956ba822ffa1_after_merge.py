def wordcloud_viz(word_cnts: pd.Series, plot_width: int, plot_height: int,) -> Panel:
    """
    Visualize the word cloud
    """  # pylint: disable=unsubscriptable-object
    ellipse_mask = np.array(
        Image.open(f"{Path(__file__).parent.parent.parent}/assets/ellipse.jpg")
    )
    wordcloud = WordCloud(background_color="white", mask=ellipse_mask)
    wordcloud.generate_from_frequencies(word_cnts)
    wcarr = wordcloud.to_array().astype(np.uint8)

    # use image_rgba following this example
    # https://docs.bokeh.org/en/latest/docs/gallery/image_rgba.html
    img = np.empty(wcarr.shape[:2], dtype=np.uint32)
    view = img.view(dtype=np.uint8).reshape((*wcarr.shape[:2], 4))
    alpha = np.full((*wcarr.shape[:2], 1), 255, dtype=np.uint8)
    view[:] = np.concatenate([wcarr, alpha], axis=2)[::-1]

    fig = figure(
        plot_width=plot_width,
        plot_height=plot_height,
        title="Word Cloud",
        x_range=(0, 1),
        y_range=(0, 1),
        toolbar_location=None,
    )
    fig.image_rgba(image=[img], x=0, y=0, dw=1, dh=1)

    fig.axis.visible = False
    fig.grid.visible = False
    return Panel(child=row(fig), title="Word Cloud")