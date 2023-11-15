    def __init__(self, data, **kwargs):
        self.mark_right = kwargs.pop('mark_right', True)
        MPLPlot.__init__(self, data, **kwargs)