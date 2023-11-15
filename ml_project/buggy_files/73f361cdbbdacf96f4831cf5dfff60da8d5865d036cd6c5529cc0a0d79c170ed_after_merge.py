    def setup_buttons(self):
        """Setup the buttons of the outline explorer widget toolbar."""
        self.fromcursor_btn = create_toolbutton(
            self, icon=ima.icon('fromcursor'), tip=_('Go to cursor position'),
            triggered=self.treewidget.go_to_cursor_position)

        buttons = [self.fromcursor_btn]
        for action in [self.treewidget.collapse_all_action,
                       self.treewidget.expand_all_action,
                       self.treewidget.restore_action,
                       self.treewidget.collapse_selection_action,
                       self.treewidget.expand_selection_action]:
            buttons.append(create_toolbutton(self))
            buttons[-1].setDefaultAction(action)
        return buttons