    def paint(self, painter, option, index):
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        style = (QApplication.style() if options.widget is None
                 else options.widget.style())

        doc = QTextDocument()
        doc.setDocumentMargin(self._margin)
        doc.setHtml(options.text)

        options.text = ""
        style.drawControl(QStyle.CE_ItemViewItem, options, painter)

        ctx = QAbstractTextDocumentLayout.PaintContext()

        textRect = style.subElementRect(QStyle.SE_ItemViewItemText, options)
        painter.save()

        # Adjustments for the file switcher
        if hasattr(options.widget, 'files_list'):
            if style.objectName() in ['oxygen', 'qtcurve', 'breeze']:
                if options.widget.files_list:
                    painter.translate(textRect.topLeft() + QPoint(4, -9))
                else:
                    painter.translate(textRect.topLeft())
            else:
                if options.widget.files_list:
                    painter.translate(textRect.topLeft() + QPoint(4, 4))
                else:
                    painter.translate(textRect.topLeft() + QPoint(2, 4))
        else:
            painter.translate(textRect.topLeft() + QPoint(0, -3))
        doc.documentLayout().draw(painter, ctx)
        painter.restore()