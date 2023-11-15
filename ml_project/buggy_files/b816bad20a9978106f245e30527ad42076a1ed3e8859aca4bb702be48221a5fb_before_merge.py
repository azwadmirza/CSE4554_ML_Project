def _hide_frame(ax):
    """Helper to hide axis frame for topomaps."""
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)