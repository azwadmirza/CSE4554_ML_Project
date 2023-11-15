    def show_at(self, position='top', *, width_ratio=0.9):
        if not self.parent():
            raise NotImplementedError("cannot show_at without parent")
        main_window = self.parent().window()
        xy = main_window.pos()
        if position == 'top':
            width = main_window.width() * width_ratio
            height = self.sizeHint().height()
            xy = xy + QPoint(main_window.width() * (1 - width_ratio) / 2, 24)
        elif position == 'bottom':
            width = main_window.width() * width_ratio
            height = self.sizeHint().height()
            y = main_window.height() - self.height() - 2
            xy = xy + QPoint(main_window.width() * (1 - width_ratio) / 2, y)
        elif position == 'left':
            width = self.sizeHint().width()
            height = main_window.height() * width_ratio
            xy = xy + QPoint(12, main_window.height() * (1 - width_ratio) / 2)
        elif position == 'right':
            width = self.sizeHint().width()
            height = main_window.height() * width_ratio
            x = main_window.width() - width - 12
            xy = xy + QPoint(x, main_window.height() * (1 - width_ratio) / 2)
        else:
            raise ValueError(
                'position must be one of ["top", "left", "bottom", "right"]'
            )

        # necessary for transparent round corners
        self.resize(self.sizeHint())
        self.setGeometry(xy.x(), xy.y(), max(width, 20), max(height, 20))
        self.show()