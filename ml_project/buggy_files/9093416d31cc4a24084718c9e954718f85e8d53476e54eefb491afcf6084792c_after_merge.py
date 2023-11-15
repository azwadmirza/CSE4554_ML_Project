    def show_list(self, completion_list, position):
        if position is None:
            # Somehow the position was not saved.
            # Hope that the current position is still valid
            self.position = self.textedit.textCursor().position()
        elif self.textedit.textCursor().position() < position:
            # hide the text as we moved away from the position
            return
        else:
            self.position = position

        # Completions are handled differently for the Internal
        # console.
        if not isinstance(completion_list[0], dict):
            self.is_internal_console = True
        self.completion_list = completion_list
        self.clear()

        icons_map = {CompletionItemKind.PROPERTY: 'attribute',
                     CompletionItemKind.VARIABLE: 'attribute',
                     CompletionItemKind.METHOD: 'method',
                     CompletionItemKind.FUNCTION: 'function',
                     CompletionItemKind.CLASS: 'class',
                     CompletionItemKind.MODULE: 'module',
                     CompletionItemKind.CONSTRUCTOR: 'method',
                     CompletionItemKind.REFERENCE: 'attribute'}

        for completion in completion_list:
            if not self.is_internal_console:
                icon = icons_map.get(completion['kind'], 'no_match')
                self.addItem(
                    QListWidgetItem(ima.icon(icon), completion['insertText']))
            else:
                # This is used by the Internal console.
                self.addItem(QListWidgetItem(completion[0]))

        self.setCurrentRow(0)

        QApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
        self.show()
        self.setFocus()
        self.raise_()

        # Retrieving current screen height
        desktop = QApplication.desktop()
        srect = desktop.availableGeometry(desktop.screenNumber(self))
        screen_right = srect.right()
        screen_bottom = srect.bottom()

        point = self.textedit.cursorRect().bottomRight()
        point = self.textedit.calculate_real_position(point)
        point = self.textedit.mapToGlobal(point)

        # Computing completion widget and its parent right positions
        comp_right = point.x() + self.width()
        ancestor = self.parent()
        if ancestor is None:
            anc_right = screen_right
        else:
            anc_right = min([ancestor.x() + ancestor.width(), screen_right])

        # Moving completion widget to the left
        # if there is not enough space to the right
        if comp_right > anc_right:
            point.setX(point.x() - self.width())

        # Computing completion widget and its parent bottom positions
        comp_bottom = point.y() + self.height()
        ancestor = self.parent()
        if ancestor is None:
            anc_bottom = screen_bottom
        else:
            anc_bottom = min([ancestor.y() + ancestor.height(), screen_bottom])

        # Moving completion widget above if there is not enough space below
        x_position = point.x()
        if comp_bottom > anc_bottom:
            point = self.textedit.cursorRect().topRight()
            point = self.textedit.mapToGlobal(point)
            point.setX(x_position)
            point.setY(point.y() - self.height())

        if ancestor is not None:
            # Useful only if we set parent to 'ancestor' in __init__
            point = ancestor.mapFromGlobal(point)
        self.move(point)

        if not self.is_internal_console:
            tooltip_point = QPoint(point)
            tooltip_point.setX(point.x() + self.width())
            tooltip_point.setY(point.y() - (3 * self.height()) // 4)
            for completion in completion_list:
                completion['point'] = tooltip_point

        if to_text_string(to_text_string(
                self.textedit.get_current_word(completion=True))):
            # When initialized, if completion text is not empty, we need
            # to update the displayed list:
            self.update_current()

        # signal used for testing
        self.sig_show_completions.emit(completion_list)