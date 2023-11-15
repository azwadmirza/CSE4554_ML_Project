    def screenshot(self):
        """Take currently displayed screen and convert to an image array.

        Returns
        -------
        image : array
            Numpy array of type ubyte and shape (h, w, 4). Index [0, 0] is the
            upper-left corner of the rendered region.
        """
        img = self.canvas.native.grabFramebuffer()
        b = img.constBits()
        h, w, c = img.height(), img.width(), 4

        # As vispy doesn't use qtpy we need to reconcile the differences
        # between the `QImage` API for `PySide2` and `PyQt5` on how to convert
        # a QImage to a numpy array.
        if API_NAME == 'PySide2':
            arr = np.array(b).reshape(h, w, c)
        else:
            b.setsize(h * w * c)
            arr = np.frombuffer(b, np.uint8).reshape(h, w, c)

        # Format of QImage is ARGB32_Premultiplied, but color channels are
        # reversed.
        arr = arr[:, :, [2, 1, 0, 3]]
        return arr