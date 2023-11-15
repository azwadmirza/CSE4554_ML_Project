    def set_data(self, data, coll_filter=None):
        """Set model data"""
        self._data = data
        data_type = get_type_string(data)

        if (coll_filter is not None and not self.remote and
                isinstance(data, (tuple, list, dict, set))):
            data = coll_filter(data)
        self.showndata = data

        self.header0 = _("Index")
        if self.names:
            self.header0 = _("Name")
        if isinstance(data, tuple):
            self.keys = list(range(len(data)))
            self.title += _("Tuple")
        elif isinstance(data, list):
            self.keys = list(range(len(data)))
            self.title += _("List")
        elif isinstance(data, set):
            self.keys = list(range(len(data)))
            self.title += _("Set")
            self._data = list(data)
        elif isinstance(data, dict):
            self.keys = sorted(list(data.keys()))
            self.title += _("Dictionary")
            if not self.names:
                self.header0 = _("Key")
        else:
            self.keys = get_object_attrs(data)
            self._data = data = self.showndata = ProxyObject(data)
            if not self.names:
                self.header0 = _("Attribute")

        if not isinstance(self._data, ProxyObject):
            self.title += (' (' + str(len(self.keys)) + ' ' +
                          _("elements") + ')')
        else:
            self.title += data_type

        self.total_rows = len(self.keys)
        if self.total_rows > LARGE_NROWS:
            self.rows_loaded = ROWS_TO_LOAD
        else:
            self.rows_loaded = self.total_rows
        self.sig_setting_data.emit()
        self.set_size_and_type()
        if len(self.keys):
            # Needed to update search scores when
            # adding values to the namespace
            self.update_search_letters()
        self.reset()