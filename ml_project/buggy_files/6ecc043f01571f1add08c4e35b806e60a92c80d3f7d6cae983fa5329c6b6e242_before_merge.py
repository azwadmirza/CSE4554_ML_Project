    def show(self):
        """Resize, show, and bring forward the window.
        """
        self._qt_window.resize(self._qt_window.layout().sizeHint())
        self._qt_window.show()
        # make sure window is not hidden, e.g. by browser window in Jupyter
        self._qt_window.raise_()