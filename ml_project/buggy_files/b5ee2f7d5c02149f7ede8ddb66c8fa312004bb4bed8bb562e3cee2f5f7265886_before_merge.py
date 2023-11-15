    def __init__(self, imdata, **kwargs):
        """Display the image for clicking."""
        from matplotlib.pyplot import figure
        self.coords = []
        self.imdata = imdata
        self.fig = figure()
        self.ax = self.fig.add_subplot(111)
        self.ymax = self.imdata.shape[0]
        self.xmax = self.imdata.shape[1]
        self.im = self.ax.imshow(imdata, aspect='auto',
                                 extent=(0, self.xmax, 0, self.ymax),
                                 picker=True, **kwargs)
        self.ax.axis('off')
        self.fig.canvas.mpl_connect('pick_event', self.onclick)
        plt_show()