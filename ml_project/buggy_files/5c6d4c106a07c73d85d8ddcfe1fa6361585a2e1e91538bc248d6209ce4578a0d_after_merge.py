    def _get_icon_rect(self, opt, text_rect):
        """Get a QRect for the icon to draw.

        Args:
            opt: QStyleOptionTab
            text_rect: The QRect for the text.

        Return:
            A QRect.
        """
        icon_size = opt.iconSize
        if not icon_size.isValid():
            icon_extent = self.pixelMetric(QStyle.PM_SmallIconSize)
            icon_size = QSize(icon_extent, icon_extent)
        icon_mode = (QIcon.Normal if opt.state & QStyle.State_Enabled
                     else QIcon.Disabled)
        icon_state = (QIcon.On if opt.state & QStyle.State_Selected
                      else QIcon.Off)
        # reserve space for favicon when tab bar is vertical (issue #1968)
        position = config.val.tabs.position
        if (position in [QTabWidget.East, QTabWidget.West] and
                config.val.tabs.favicons.show != 'never'):
            tab_icon_size = icon_size
        else:
            actual_size = opt.icon.actualSize(icon_size, icon_mode, icon_state)
            tab_icon_size = QSize(
                min(actual_size.width(), icon_size.width()),
                min(actual_size.height(), icon_size.height()))

        icon_top = text_rect.center().y() + 1 - tab_icon_size.height() / 2
        icon_rect = QRect(QPoint(text_rect.left(), icon_top), tab_icon_size)
        icon_rect = self._style.visualRect(opt.direction, opt.rect, icon_rect)
        return icon_rect