    def _update_palette(self, palette):
        """Update widget color palette.

        Parameters
        ----------
        palette : qtpy.QtGui.QPalette
            Color palette for each widget state (Active, Disabled, Inactive).
        """
        # set window styles which don't use the primary stylesheet
        # FIXME: this is a problem with the stylesheet not using properties
        self._status_bar.setStyleSheet(
            template(
                'QStatusBar { background: {{ background }}; '
                'color: {{ text }}; }',
                **palette,
            )
        )
        self._qt_center.setStyleSheet(
            template('QWidget { background: {{ background }}; }', **palette)
        )
        self._qt_window.setStyleSheet(template(self.raw_stylesheet, **palette))