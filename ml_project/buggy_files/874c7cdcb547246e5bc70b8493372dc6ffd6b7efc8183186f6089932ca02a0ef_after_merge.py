    def setup_file_list(self, filter_text, current_path):
        """Setup list widget content for file list display."""
        short_paths = shorten_paths(self.paths, self.save_status)
        paths = self.paths
        icons = self.icons
        results = []
        trying_for_line_number = ':' in filter_text

        # Get optional line number
        if trying_for_line_number:
            filter_text, line_number = filter_text.split(':')
            if line_number == '':
                line_number = None
            # Get all the available filenames
            scores = get_search_scores('', self.filenames,
                                       template="<b>{0}</b>")
        else:
            line_number = None
            # Get all available filenames and get the scores for
            # "fuzzy" matching
            scores = get_search_scores(filter_text, self.filenames,
                                       template="<b>{0}</b>")

        # Get max width to determine if shortpaths should be used
        max_width = self.get_item_size(paths)[0]
        self.fix_size(paths)

        # Build the text that will appear on the list widget
        rich_font = CONF.get('appearance', 'rich_font/size', 10)
        if sys.platform == 'darwin':
            path_text_font_size = rich_font
            filename_text_font_size = path_text_font_size + 2
        elif os.name == 'nt':
            path_text_font_size = rich_font
            filename_text_font_size = path_text_font_size + 1
        elif is_ubuntu():
            path_text_font_size = rich_font - 2
            filename_text_font_size = path_text_font_size + 1
        else:
            path_text_font_size = rich_font
            filename_text_font_size = path_text_font_size + 1

        for index, score in enumerate(scores):
            text, rich_text, score_value = score
            linecount = ""
            if score_value != -1:
                fileName = rich_text.replace('&', '')
                if trying_for_line_number:
                    linecount = "[{0:} {1:}]".format(self.line_count[index],
                                                     _("lines"))
                if max_width > self.list.width():
                    path = short_paths[index]
                else:
                    path = paths[index]

                title = self.widgets[index][1].get_plugin_title().split(
                    ' - ')[0]

                text_item = self._TEMPLATE.format(
                    width=self._MIN_WIDTH, height=self._HEIGHT, title=fileName,
                    section=title, description=path, padding=self._PADDING,
                    shortcut=linecount, **self._STYLES)

                if ((trying_for_line_number and self.line_count[index] != 0)
                        or not trying_for_line_number):
                    results.append((score_value, index, text_item))

        # Sort the obtained scores and populate the list widget
        self.filtered_path = []
        plugin = None
        separator = self._TEMPLATE_SEP.format(
            width=self.list.width()-20, height=self._HEIGHT_SEP,
            **self._STYLES_SEP)
        for result in sorted(results):
            index = result[1]
            path = paths[index]
            if sys.platform == 'darwin':
                scale_factor = 0.9
            elif os.name == 'nt':
                scale_factor = 0.8
            elif is_ubuntu():
                scale_factor = 0.7
            else:
                scale_factor = 0.9
            icon = ima.get_icon_by_extension(path, scale_factor)
            text = ''
            try:
                title = self.widgets[index][1].get_plugin_title().split(' - ')
                if plugin != title[0]:
                    plugin = title[0]
                    text = separator
                    item = QListWidgetItem(text)
                    item.setToolTip(path)
                    item.setSizeHint(QSize(0, 25))
                    item.setFlags(Qt.ItemIsEditable)
                    self.list.addItem(item)
                    self.filtered_path.append(path)
            except:
                # The widget using the fileswitcher is not a plugin
                pass
            text = ''
            text += result[-1]
            item = QListWidgetItem(icon, text)
            item.setToolTip(path)
            item.setSizeHint(QSize(0, 25))
            self.list.addItem(item)
            self.filtered_path.append(path)

        # To adjust the delegate layout for KDE themes
        self.list.files_list = True

        # Move selected item in list accordingly and update list size
        if current_path in self.filtered_path:
            self.set_current_row(self.filtered_path.index(current_path))
        elif self.filtered_path:
            self.set_current_row(0)

        # If a line number is searched look for it
        self.line_number = line_number
        self.goto_line(line_number)