    def select_element(self, element):
        """
        Select an element from the Namespace view.
        The element is selected. After this an action may be executed,
        such as OpenModelElement, which will try to open the element (if it's
        a Diagram).
        """
        path = Gtk.TreePath.new_from_indices(
            self._namespace.get_model().path_from_element(element)
        )
        # Expand the first row:
        if len(path.get_indices()) > 1:
            self._namespace.expand_row(path=path, open_all=False)
        selection = self._namespace.get_selection()
        selection.select_path(path)
        self._on_view_cursor_changed(self._namespace)