    def set_dataset(self, data, tid=None):
        """Set the input dataset."""
        self.closeContext()
        if data is not None:
            if tid in self._inputs:
                # update existing input slot
                slot = self._inputs[tid]
                view = slot.view
                # reset the (header) view state.
                view.setModel(None)
                view.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
            else:
                view = QTableView()
                view.setSortingEnabled(True)
                view.setHorizontalScrollMode(QTableView.ScrollPerPixel)

                if self.select_rows:
                    view.setSelectionBehavior(QTableView.SelectRows)

                header = view.horizontalHeader()
                header.setSectionsMovable(True)
                header.setSectionsClickable(True)
                header.setSortIndicatorShown(True)
                header.setSortIndicator(-1, Qt.AscendingOrder)

                # QHeaderView does not 'reset' the model sort column,
                # because there is no guaranty (requirement) that the
                # models understand the -1 sort column.
                def sort_reset(index, order):
                    if view.model() is not None and index == -1:
                        view.model().sort(index, order)

                header.sortIndicatorChanged.connect(sort_reset)

            view.dataset = data
            self.tabs.addTab(view, getattr(data, "name", "Data"))

            self._setup_table_view(view, data)
            slot = TableSlot(tid, data, table_summary(data), view)
            view._input_slot = slot
            self._inputs[tid] = slot

            self.tabs.setCurrentIndex(self.tabs.indexOf(view))

            self.set_info(slot.summary)

            if isinstance(slot.summary.len, concurrent.futures.Future):
                def update(f):
                    QMetaObject.invokeMethod(
                        self, "_update_info", Qt.QueuedConnection)

                slot.summary.len.add_done_callback(update)

        elif tid in self._inputs:
            slot = self._inputs.pop(tid)
            view = slot.view
            view.hide()
            view.deleteLater()
            self.tabs.removeTab(self.tabs.indexOf(view))

            current = self.tabs.currentWidget()
            if current is not None:
                self.set_info(current._input_slot.summary)

        self.tabs.tabBar().setVisible(self.tabs.count() > 1)
        self.openContext(data)

        if self.__pending_selected_rows is not None:
            self.selected_rows = self.__pending_selected_rows
            self.__pending_selected_rows = None
        else:
            self.selected_rows = []

        if self.__pending_selected_cols is not None:
            self.selected_cols = self.__pending_selected_cols
            self.__pending_selected_cols = None
        else:
            self.selected_cols = []

        self.set_selection()
        self.commit()