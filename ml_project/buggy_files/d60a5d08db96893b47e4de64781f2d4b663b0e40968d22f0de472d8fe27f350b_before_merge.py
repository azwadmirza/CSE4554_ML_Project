def render_missing(
    itmdt: Intermediate,
    plot_width: int = 500,
    plot_height: int = 500,
    palette: Optional[Sequence[str]] = None,
) -> LayoutDOM:
    """
    @Jinglin write here
    """
    if itmdt.visual_type == "missing_spectrum":
        return render_missing_spectrum(itmdt, plot_width, plot_height)
    elif itmdt.visual_type == "missing_impact_1vn":
        return render_missing_impact_1vn(itmdt, plot_width, plot_height)
    elif itmdt.visual_type == "missing_impact_1v1":
        return render_missing_impact_1v1(itmdt, plot_width, plot_height)
    elif itmdt.visual_type == "missing_spectrum_heatmap":
        return render_missing_heatmap(
            itmdt, plot_width, plot_height, palette or BIPALETTE
        )

    else:
        raise UnreachableError