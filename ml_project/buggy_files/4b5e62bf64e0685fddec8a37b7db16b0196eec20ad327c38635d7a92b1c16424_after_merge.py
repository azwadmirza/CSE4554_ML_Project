    def __init__(self, parent, name, series, **kargs):
        axisItems = {'bottom': DateAxisItem('bottom')}
        super(TimeSeriesPlot, self).__init__(parent=parent, title=name, axisItems=axisItems, **kargs)
        self.getPlotItem().showGrid(x=True, y=True)
        self.setBackground('#202020')
        self.setAntialiasing(True)
        self.setMenuEnabled(False)

        self.plot_data = {}
        self.plots = []
        self.series = series
        self.last_timestamp = 0

        legend = pg.LegendItem((150, 25 * len(series)), offset=(150, 30))
        legend.setParentItem(self.graphicsItem())

        for serie in series:
            plot = self.plot(**serie)
            self.plots.append(plot)
            legend.addItem(plot, serie['name'])

        # Limit the date range
        self.setLimits(xMin=BITTORRENT_BIRTHDAY, xMax=time.time() + YEAR_SPACING)