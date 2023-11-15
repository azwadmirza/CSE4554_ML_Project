    def tree_view_rename_selected(self):
        view = self._namespace
        element = view.get_selected_element()
        if element is not None:
            path = view.get_model().path_from_element(element)
            column = view.get_column(0)
            cell = column.get_cells()[1]
            cell.set_property("editable", 1)
            cell.set_property("text", element.name)
            view.set_cursor(path, column, True)
            cell.set_property("editable", 0)