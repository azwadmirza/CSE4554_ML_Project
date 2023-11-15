    def __init__(self, ax, raster_source, **kwargs):
        self.raster_source = raster_source
        super(SlippyImageArtist, self).__init__(ax, **kwargs)
        self.cache = []

        ax.figure.canvas.mpl_connect('button_press_event', self.on_press)
        ax.figure.canvas.mpl_connect('button_release_event', self.on_release)

        self.on_release()