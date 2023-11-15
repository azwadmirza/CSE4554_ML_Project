    def __eventually_raise_help(self, text, force=False):
        index = self.source_combo.currentIndex()
        if hasattr(self.main, 'tabifiedDockWidgets'):
            # 'QMainWindow.tabifiedDockWidgets' was introduced in PyQt 4.5
            if (self.dockwidget and (force or self.dockwidget.isVisible()) and
                    not self.ismaximized and
                    (force or text != self._last_texts[index])):
                dockwidgets = self.main.tabifiedDockWidgets(self.dockwidget)
                if (self.console.dockwidget not in dockwidgets and
                        self.ipyconsole is not None and
                        self.ipyconsole.dockwidget not in dockwidgets):
                    self.dockwidget.show()
                    self.dockwidget.raise_()
        self._last_texts[index] = text