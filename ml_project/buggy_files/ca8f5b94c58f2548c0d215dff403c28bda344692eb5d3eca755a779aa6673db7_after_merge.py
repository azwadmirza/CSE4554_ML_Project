    def scale_image(self):
        """Scale the image size."""
        fwidth = self.figcanvas.fwidth
        fheight = self.figcanvas.fheight

        # Don't auto fit plotting
        if not self.auto_fit_plotting:
            new_width = int(fwidth * self._scalestep ** self._scalefactor)
            new_height = int(fheight * self._scalestep ** self._scalefactor)

        # Auto fit plotting
        # Scale the image to fit the figviewer size while respecting the ratio.
        else:
            size = self.size()
            style = self.style()
            width = (size.width() -
                     style.pixelMetric(QStyle.PM_LayoutLeftMargin) -
                     style.pixelMetric(QStyle.PM_LayoutRightMargin))
            height = (size.height() -
                      style.pixelMetric(QStyle.PM_LayoutTopMargin) -
                      style.pixelMetric(QStyle.PM_LayoutBottomMargin))
            self.figcanvas.setToolTip('')
            try:
                if (fwidth / fheight) > (width / height):
                    new_width = int(width)
                    new_height = int(width / fwidth * fheight)
                else:
                    new_height = int(height)
                    new_width = int(height / fheight * fwidth)
            except ZeroDivisionError:
                icon = ima.icon('broken_image')
                self.figcanvas._qpix_orig = icon.pixmap(fwidth, fheight)
                self.figcanvas.setToolTip(
                    _('The image is broken, please try to generate it again'))
                new_width = fwidth
                new_height = fheight

        if self.figcanvas.size() != QSize(new_width, new_height):
            self.figcanvas.setFixedSize(new_width, new_height)
            self.sig_zoom_changed.emit(self.get_scaling())